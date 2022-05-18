from DCN import DCN
import tensorflow as tf
import sys
from pathlib import Path
import time
from itertools import chain, combinations, product
import json
from tensorboard.plugins.hparams import api as hp
import pandas as pd
import numpy as np

# Loading data
interactions = pd.read_csv('database_contents.csv')

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
    'avg_sentiment': x['avg_sentiment'],
    'affinity': x['affinity'],
})

n_inter = len(interactions)

tf.random.set_seed(42)
shuffled = interactions
train = shuffled.take(int(n_inter*0.8))
test = shuffled.skip(int(n_inter*0.8)).take(int(n_inter*0.2))

cat_features = ['day_of_week', 'article_id', 'device_id', 'title', 'section', 'location']
cont_features = ['time', 'release_date', 'avg_sentiment']
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
    'str_features': ['section', 'location'],
    'int_features': ['day_of_week'],
    'text_features': ['title'],
    'cont_features': ['time', 'release_date', 'avg_sentiment'],
    'disc_features': ['time', 'release_date', 'avg_sentiment']
}

def powerset(s:list):
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

dl = {k:[list(i) for i in powerset(v)] for k,v in feature_dict.items()}

appended = dl['str_features']
for i in range(len(appended)):
    appended[i].extend(['article_id', 'device_id'])

dl['str_features'] = appended

ld = [dict(zip(dl.keys(), items)) 
        for items in product(*(dl.values()))]

perm_dicts = [json.dumps(i) for i in ld]

deep_layers = [json.dumps(i) for i in [[], [64,64], [128, 128], [64, 64, 128], [64, 128, 256]]]


HP_FEATURES = hp.HParam('feature_dicts', hp.Discrete(perm_dicts))
HP_CROSS_BOOL = hp.HParam('use_cross_layer', hp.Discrete([True, False]))
HP_N_CROSS = hp.HParam('n_cross_layers', hp.Discrete([1,2,3]))
HP_DEEP_SIZE = hp.HParam('deep_layer_size', hp.Discrete(deep_layers))

METRIC_RMSE = tf.keras.metrics.RootMeanSquaredError('RMSE')

with tf.summary.create_file_writer('logs/hparam_tuning').as_default():
  hp.hparams_config(
    hparams=[HP_FEATURES, HP_CROSS_BOOL, HP_N_CROSS, HP_DEEP_SIZE],
    metrics=[hp.Metric(METRIC_RMSE.name, display_name='RMSE')],
  )

cached_train = train.shuffle(n_inter).batch(128).cache()
cached_test = test.shuffle(n_inter).batch(64).cache()

def train_test_model(hparams: dict):
    model = DCN(
        feature_dict=json.loads(hparams[HP_FEATURES]), 
        use_cross_layer=hparams[HP_CROSS_BOOL], 
        n_cross_layers=hparams[HP_N_CROSS],
        deep_layer_size=json.loads(hparams[HP_DEEP_SIZE]),
        vocabularies=vocabularies
        )
    
    model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))
    model.fit(cached_train, epochs=10)
    rmse, _, _, _ = model.evaluate(cached_test)
    return rmse


def run(run_dir, hparams):
    with tf.summary.create_file_writer(run_dir).as_default():
        hp.hparams(hparams)  # record the values used in this trial
        rmse = train_test_model(hparams)
        tf.summary.scalar(METRIC_RMSE.name, rmse, step=1)

session_num = 0

for f_dict in HP_FEATURES.domain.values:
    for cross_bool in HP_CROSS_BOOL.domain.values:
        for n_layers in HP_N_CROSS.domain.values:
            for layer_size in HP_DEEP_SIZE.domain.values:
                hparams = {
                    HP_FEATURES: f_dict,
                    HP_CROSS_BOOL: cross_bool,
                    HP_N_CROSS: n_layers,
                    HP_DEEP_SIZE: layer_size
                }
                run_name = "run-%d" % session_num
                print('--- Starting trial: %s' % run_name)
                print({h.name: hparams[h] for h in hparams})
                run('logs/hparam_tuning/' + run_name, hparams)
                session_num += 1

