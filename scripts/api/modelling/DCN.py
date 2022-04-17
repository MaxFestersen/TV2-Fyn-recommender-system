from pathlib import Path
import time
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np
from tensorflow.keras import Sequential
from tensorflow.keras.layers import StringLookup, IntegerLookup, Embedding, Dense, Discretization, Normalization, TextVectorization, GlobalAveragePooling1D
import os
import sys

sys.path.append(str(Path(__file__).parents[1]))
from utility.data_optimized import allUsers

os.environ['TF_XLA_FLAGS'] = '--tf_xla_cpu_global_jit'

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

feature_dict = {
    'str_features': ['article_id', 'device_id', 'section', 'location'],
    'int_features': ['day_of_week'],
    'text_features': ['title'],
    'cont_features': ['time', 'release_date'],
    'disc_features': ['time', 'release_date']
}

class DCN(tfrs.Model):

    def __init__(self, feature_dict: dict, use_cross_layer: bool, deep_layer_size: list, projection_dim=None):
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
            ], name=feature)
        
        # Create embeddings for int features
        for feature in self.int_features:
            vocabulary = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                IntegerLookup(
                    vocabulary=vocabulary, mask_token=None),
                Embedding(len(vocabulary) + 1, self.embedding_dimension)
            ], name=feature)

        # Create embeddings for text features
        for feature in self.text_features:
            vectorizer = TextVectorization(
                max_tokens=self.max_tokens
            )
            self._embeddings[feature] = Sequential([
                vectorizer,
                Embedding(self.max_tokens, self.embedding_dimension, mask_zero=True),
                GlobalAveragePooling1D()
            ], name=feature)
            vectorizer.adapt(vocabularies[feature])
        
        # Create embeddings for continuous features
        for feature in self.cont_features:
            vocab = vocabularies[feature][0]
            normalized = Normalization(
                axis=None,
                name=feature
            )
            normalized.adapt(vocab)
            self._embeddings_cont[feature] = normalized
        
        # Create embeddings for discrete features
        for feature in self.disc_features:
            vocab = vocabularies[feature][1]
            self._embeddings[feature] = Sequential([
                Discretization(vocab.tolist()),
                Embedding(len(vocab) + 1, self.embedding_dimension)
            ], name=feature)
        
        if use_cross_layer:
            self._cross_layer = tfrs.layers.dcn.Cross(
                projection_dim=projection_dim,
                kernel_initializer='glorot_uniform'
            )
        else:
            self._cross_layer = None
        
        self._deep_layers = [Dense(layer_size, activation='relu') for layer_size in deep_layer_size]
        
        self._logit_layer = Dense(1)

        self.task = tfrs.tasks.Ranking(
            loss = tf.keras.losses.MeanSquaredError(),
            metrics = [tf.keras.metrics.RootMeanSquaredError("RMSE")]
        )

    def call(self, inputs):
        embeddings = []
        for feature in self._all_features:
            embedding_fn = self._embeddings[feature]
            embeddings.append(embedding_fn(inputs[feature]))
        
        for feature in self.cont_features:
            embedding_fn = self._embeddings_cont[feature]
            embeddings.append(tf.reshape(embedding_fn(inputs[feature]), (-1,1)))

        x = tf.concat(embeddings, axis=1)

        # Build Cross Network
        if self._cross_layer is not None:
            x = self._cross_layer(x)
        
        # Build Deep Network
        for deep_layer in self._deep_layers:
            x = deep_layer(x)
        
        return self._logit_layer(x)

    def compute_loss(self, inputs, training: bool = False):
        labels = inputs.pop('affinity')
        scores = self(inputs)
        return self.task(
            labels=labels,
            predictions=scores
        )


cached_train = train.shuffle(n_inter).batch(10).cache()
cached_test = test.shuffle(n_inter).batch(5).cache()

model = DCN(feature_dict, True, [64, 32])

model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

logdir="logs/fit/" + str(time.time())
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)

model.fit(cached_train,
 epochs=3,
 callbacks=[tensorboard_callback])

# model.evaluate(cached_test, return_dict=True)

# tf.saved_model.save(model, 'tfserving/models/DCN/{}'.format(int(time.time())))
