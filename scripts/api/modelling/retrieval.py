from pathlib import Path
import time
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import StringLookup, IntegerLookup, Embedding, Dense, Discretization, Normalization, TextVectorization, GlobalAveragePooling1D
import sys

sys.path.append(str(Path(__file__).parents[1]))
from utility.data_optimized import allUsers

interactions = allUsers().interactions()

interactions = tf.data.Dataset.from_tensor_slices(dict(interactions))

interactions = interactions.map(lambda x: {
    'day_of_week': x['day_of_week'],
    'time': x['time'],
    'device_id': x['device_id'],
    'article_id': x['article_id'],
    'title': x['title'],
    'section': x['section'],
    'location': x['location'],
    'release_date': x['release_date'],
    'affinity': x['affinity'],
})

candidates = interactions.map(lambda x: {
    'article_id': x['article_id'],
    'section': x['section'],
    'location': x['location'],
    'title': x['title'],
    'release_date': x['release_date']

})

n_inter = len(interactions)

tf.random.set_seed(42)
shuffled = interactions.shuffle(n_inter, seed=42, reshuffle_each_iteration=False)
train = shuffled.take(int(n_inter*0.8))
test = shuffled.skip(int(n_inter*0.8)).take(int(n_inter*0.2))

cat_features = ['day_of_week', 'article_id', 'device_id', 'title', 'section', 'location']
cont_features = ['time', 'release_date']
vocabularies = {}

for feature in cat_features:
    vocab = interactions.batch(1_000_000).map(lambda x: x[feature])
    vocabularies[feature] = np.unique(np.concatenate(list(vocab)))

for feature in cont_features:
    cont =  np.concatenate(list(interactions.map(lambda x: x[feature]).batch(1_000_000)))
    cont_bucket = np.linspace(
    cont.min(), cont.max(), num=1000
    )
    vocabularies[feature] = [cont, cont_bucket]

feature_dicts = {
    'query':
    {
        'str_features': ['device_id'],
        'int_features': ['day_of_week'],
        'text_features': [],
        'cont_features': ['time',],
        'disc_features': ['time']
    }, 
    'candidate':
    {
        'str_features': ['article_id', 'section', 'location',],
        'int_features': [],
        'text_features': ['title'],
        'cont_features': ['release_date'],
        'disc_features': ['release_date']
    }
}

class BuildModel(tf.keras.Model):

    def __init__(self, feature_dict:dict):
        super().__init__()
    
        self.embedding_dimension = 32
        self.max_tokens = 10_000

        self.str_features = feature_dict.get('str_features')
        self.int_features = feature_dict.get('int_features')
        self.text_features = feature_dict.get('text_features')
        self.cont_features = feature_dict.get('cont_features')
        self.disc_features = feature_dict.get('disc_features')
        
        self._all_features = self.str_features + self.int_features + self.text_features + self.cont_features + self.disc_features
        self._embeddings = {}
        self._embeddings_cont = {}

        # Create embeddings for str features
        for feature in self.str_features:
            vocabulary = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                StringLookup(
                    vocabulary=vocabulary, mask_token=None),
                Embedding(len(vocabulary) + 1, self.embedding_dimension)
            ])
        
        # Create embeddings for int features
        for feature in self.int_features:
            vocabulary = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                IntegerLookup(
                    vocabulary=vocabulary, mask_token=None),
                Embedding(len(vocabulary) + 1, self.embedding_dimension)
            ])

        # Create embeddings for text features
        for feature in self.text_features:
            vectorizer = TextVectorization(
                max_tokens=self.max_tokens
            )
            self._embeddings[feature] = Sequential([
                vectorizer,
                Embedding(self.max_tokens, self.embedding_dimension, mask_zero=True),
                GlobalAveragePooling1D()
            ])
            vectorizer.adapt(vocabularies[feature])
        
        # Create embeddings for continuous features
        for feature in self.cont_features:
            vocab = vocabularies[feature][0]
            normalized = Normalization(
                axis=None
            )
            normalized.adapt(vocab)
            self._embeddings_cont[feature] = normalized
        
        # Create embeddings for discrete features
        for feature in self.disc_features:
            vocab = vocabularies[feature][1]
            self._embeddings[feature] = Sequential([
                Discretization(vocab.tolist()),
                Embedding(len(vocab) + 1, self.embedding_dimension)
            ])
        
    def call(self, inputs):
        embeddings = []
        for feature in self._all_features:
            embedding_fn = self._embeddings[feature]
            embeddings.append(embedding_fn(inputs[feature]))
        
        for feature in self.cont_features:
            embedding_fn = self._embeddings_cont[feature]
            embeddings.append(tf.reshape(embedding_fn(inputs[feature]), (-1,1)))

        x = tf.concat(embeddings, axis=1)
        return x

class RetrievalModel(tfrs.models.Model):

    def __init__(self, feature_dicts:dict):
        super().__init__()

        self._query_features = feature_dicts.get('query')
        self._candidate_features = feature_dicts.get('candidate')

        self.query_model = Sequential([
            BuildModel(self._query_features),
            Dense(32)
        ])

        self.candidate_model = Sequential([
            BuildModel(self._candidate_features),
            Dense(32)
        ])
        
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=candidates.batch(128).map(self.candidate_model),
            ),
        )

    def compute_loss(self, inputs, training: bool = False) -> tf.Tensor:
        query_features = list(set().union(*self._query_features.values()))
        query_embeddings = self.query_model(dict(zip(
            query_features,
            [inputs[i] for i in query_features]
        )))

        candidate_features = list(set().union(*self._candidate_features.values()))
        candidate_embeddings = self.candidate_model(dict(zip(
            candidate_features,
            [inputs[i] for i in candidate_features]
        )))

        return self.task(query_embeddings, candidate_embeddings)

cached_train = train.shuffle(n_inter).batch(10).cache()
cached_test = test.shuffle(n_inter).batch(5).cache()

model = RetrievalModel(feature_dicts=feature_dicts)

model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))
model.fit(cached_train, epochs=3)

model.evaluate(cached_test, return_dict=True)


index = tfrs.layers.factorized_top_k.ScaNN(model.query_model, k=3, num_leaves=5)

index.index_from_dataset(
    candidates.batch(128).map(model.candidate_model)
)

index.index_from_dataset(
    tf.data.Dataset.zip(
        (   
            candidates.batch(128).map(lambda x: x['article_id']),
            candidates.batch(128).map(model.candidate_model)
        )
    )
)

_, ids = index({'day_of_week': np.array([1]), 'time': np.array([85646]), 'device_id': np.array(['1649634234511-660'])})

