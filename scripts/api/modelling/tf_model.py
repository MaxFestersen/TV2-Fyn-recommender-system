from typing import Dict, Text
from pathlib import Path
import tensorflow as tf
import tensorflow_recommenders as tfrs
import numpy as np
from tensorflow.keras import Sequential, Model
from tensorflow.keras.layers import StringLookup, Embedding, Layer, Dense, Discretization, Normalization, TextVectorization, GlobalAveragePooling1D
import sys

sys.path.append(str(Path(__file__).parents[1]))
from utility.data_optimized import allUsers

interactions = allUsers().interactions()

interactions = tf.data.Dataset.from_tensor_slices(dict(interactions))
interactions = interactions.map(lambda x: {
    'deviceID': x['device_id'],
    'articleID': x['article_id'],
    'affinity': x['affinity'],
    'accessed': x['date'],
    'title': x['title'],
    'published': x['release_date']
})

n_inter = len(interactions)

tf.random.set_seed(42)
shuffled = interactions.shuffle(n_inter, seed=42, reshuffle_each_iteration=False)

train = shuffled.take(int(n_inter*0.8))
test = shuffled.skip(int(n_inter*0.8)).take(int(n_inter*0.2))

batch_size = 10

titles = np.unique(np.concatenate(list(interactions.batch(batch_size).map(lambda x: x['title']))))
unique_articles = np.unique(np.concatenate(list(interactions.batch(batch_size).map(lambda x: x['articleID']))))
unique_users = np.unique(np.concatenate(list(interactions.batch(batch_size).map(lambda x: x['deviceID']))))

acc_time = np.concatenate(list(interactions.map(lambda x: x['accessed']).batch(batch_size)))
acc_time_bucket = np.linspace(
    acc_time.min(), acc_time.max(), num=1000
)

pub_time = np.concatenate(list(interactions.map(lambda x: x['published']).batch(batch_size)))
pub_time_bucket = np.linspace(
    pub_time.min(), pub_time.max(), num=1000
)

class UserModel(Model):
    def __init__(self, use_acc_time):
        super().__init__()

        self._use_acc_time = use_acc_time

        embedding_dimension = 32
        self.user_embedding: Layer = Sequential([
            StringLookup(
                vocabulary=unique_users, mask_token=None),
            Embedding(len(unique_users) + 1, embedding_dimension)
        ])
        if use_acc_time:
            self.acc_time_embedding: Layer = Sequential([
                Discretization(acc_time_bucket.tolist()),
                Embedding(len(acc_time_bucket) + 1, embedding_dimension),
            ])
            self.normal_acc_time = Normalization(
                axis=None
            )
            self.normal_acc_time.adapt(acc_time)
    def call(self, inputs):
        if not self._use_acc_time:
            return self.user_embedding(inputs['deviceID'])
        return tf.concat([
            self.user_embedding(inputs['deviceID']),
            self.acc_time_embedding(inputs['accessed']),
            tf.reshape(self.normal_acc_time(inputs['accessed']), (-1, 1)),
        ], axis=1)

class ArticleModel(Model):
    def __init__(self, use_titles, use_pub_time):
        super().__init__()
        self._use_titles = use_titles
        self._use_pub_time = use_pub_time
        max_tokens = 10_000
        embedding_dimension = 32
    
        self.article_embedding: Layer = Sequential([
            StringLookup(
                vocabulary=unique_articles, mask_token=None),
            Embedding(len(unique_articles) + 1, embedding_dimension)
        ])
        if use_titles:
            self.title_vectorizer = TextVectorization(
                max_tokens=max_tokens
            )
            self.title_text_embedding: Layer = Sequential([
                self.title_vectorizer,
                Embedding(max_tokens, 32, mask_zero=True),
                GlobalAveragePooling1D(),
            ])
            self.title_vectorizer.adapt(titles)
        
        if use_pub_time:
            self.pub_time_embedding: Layer = Sequential([
                Discretization(pub_time_bucket.tolist()),
                Embedding(len(pub_time_bucket) + 1, embedding_dimension),
            ])
            self.normal_pub_time = Normalization(
                axis=None
            )
            self.normal_pub_time.adapt(pub_time)

    def call(self, inputs: Dict[Text, tf.Tensor]) -> tf.Tensor:
        if self._use_titles and self._use_pub_time:
            return tf.concat([
            self.article_embedding(inputs['articleID']),
            self.title_text_embedding(inputs['title']),
            self.pub_time_embedding(inputs['published']),
            tf.reshape(self.normal_pub_time(inputs['published']), (-1, 1)),
        ], axis=1)
        elif self._use_pub_time:
            return tf.concat([
                self.article_embedding(inputs['articleID']),
                self.pub_time_embedding(inputs['published']),
                tf.reshape(self.normal_pub_time(inputs['published']), (-1, 1)),
            ], axis=1)
        elif self._use_titles:
            return tf.concat([
            self.article_embedding(inputs['articleID']),
            self.title_text_embedding(inputs['title']),
        ], axis=1)
        return self.article_embedding(inputs['articleID'])

class TV2FynRecommenderModel(tfrs.Model):
    def __init__(self, rank_weight: float, retrieve_weight: float, use_acc_time: bool=False, use_pub_time: bool=False, use_titles: bool=False):
        super().__init__()

        self.user_model: Layer = Sequential([
            UserModel(use_acc_time),
            Dense(32),
        ])
        self.article_model: Layer = Sequential([
            ArticleModel(use_titles, use_pub_time),
            Dense(32),
        ])

        self.retrieval_task: Layer = tfrs.tasks.Retrieval(
            metrics = tfrs.metrics.FactorizedTopK(
                candidates=interactions.batch(batch_size).map(self.article_model)
            )
        )
        self.retrieval_weight = retrieve_weight

        self.ranking_model: Layer = Sequential([
            Dense(256, activation='relu'),
            Dense(128, activation='relu'),
            Dense(1),
        ])

        self.ranking_task: Layer = tfrs.tasks.Ranking(
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=[tf.keras.metrics.RootMeanSquaredError()],
        )
        self.ranking_weight = rank_weight
    
    def call(self, inputs: Dict[Text, tf.Tensor]) -> tf.Tensor:
        user_model = self.user_model(inputs)
        article_model = self.article_model(inputs)
        return (
            user_model,
            article_model,
            self.ranking_model(
                tf.concat([user_model, article_model], axis=1)
            ),
        )

    def compute_loss(self, inputs: Dict[Text, tf.Tensor], training: bool = False) -> tf.Tensor:
        
        rankings = inputs.pop('affinity')
        
        user_embeddings, article_embeddings, ranking_predictions = self(inputs)

        retrieval_loss = self.retrieval_task(user_embeddings, article_embeddings)
        ranking_loss = self.ranking_task(
            labels = rankings,
            predictions=ranking_predictions
        )
        return (self.ranking_weight*ranking_loss 
                + self.retrieval_weight * retrieval_loss)

model = TV2FynRecommenderModel(1.0, 1.0, True, True, True)
model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

cached_train = train.shuffle(len(interactions)).batch(batch_size).cache()
cached_test = test.batch(int(batch_size*0.5)).cache()

model.fit(cached_train, epochs=3)

model.evaluate(cached_test, return_dict=True)