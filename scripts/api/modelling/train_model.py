from DCN import DCN
import tensorflow as tf
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
import time
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime
from utility.data_optimized import allUsers

os.environ['TF_XLA_FLAGS'] = '--tf_xla_cpu_global_jit'

# Loading data
# interactions = pd.read_csv('database_contents.csv', index_col=False).iloc[:, 1:].dropna()

interactions = allUsers().interactions().dropna()

# Creating column context_id containing list of previously visited article_ids
interactions['week_n'] = interactions['date'].apply(lambda x: datetime.fromtimestamp(x).isocalendar().week)
interactions['context_id'] = interactions.sort_values('date').groupby(['device_id', 'week_n'])['article_id'].apply(lambda x: (x + ' ').cumsum().str.strip())
interactions['context_id'] = interactions['context_id'].apply(lambda x: list(x.split(' ')))
[lid.remove(id) for lid,id in zip(interactions.context_id, interactions.article_id) if id in lid]
n = max(interactions['context_id'].apply(len))
[lid.extend(['']* (n - len(lid))) for lid in interactions.context_id]

def detect_outlier(data):
    outliers=[]
    threshold=3
    mean = np.mean(data)
    std = np.std(data)
    
    
    for y in data:
        z_score= (y - mean)/std
        if np.abs(z_score) > threshold:
            outliers.append(y)
    return outliers

interactions = interactions[interactions.affinity < min(detect_outlier(interactions.affinity))]

interactions = interactions.groupby('device_id').filter(lambda d: len(d) > 1)

train, test = train_test_split(interactions, test_size=len(np.unique(interactions['device_id'])), random_state=42, stratify=interactions[['device_id']])

test, val = train_test_split(test, test_size=0.5, random_state=42)

# Converting from Pandas dataframe to tensorflow dataset
interactions = tf.data.Dataset.from_tensor_slices(interactions.to_dict('list'))

train = tf.data.Dataset.from_tensor_slices(train.to_dict('list'))
test = tf.data.Dataset.from_tensor_slices(test.to_dict('list'))
val = tf.data.Dataset.from_tensor_slices(val.to_dict('list'))

train = train.map(lambda x: {
    'section': x['section'],
    'location': x['location'],
    'article_id': x['article_id'],
    'device_id': x['device_id'],
    'context_id': x['context_id'],
    'affinity': x['affinity']
})

# Creating vocabularies for embeddings
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

# context_id has the same vocab as article_id
vocabularies['context_id'] = vocabularies['article_id']

# Setting up feature dict only with features tried in combinations
feature_dict = {
    'str_features': ['section', 'location', 'article_id', 'device_id'],
    'int_features': [],
    'text_features': [],
    'cont_features': [],
    'disc_features': [],
    'seq_features': ['context_id']
}

# Caching dataset
cached_train = train.shuffle(len(train)).batch(128).cache()
cached_test = test.shuffle(len(test)).batch(64).cache()
cached_val = val.shuffle(len(val)).batch(64).cache()

# Callbacks
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="./logs")

checkpoint_filepath = './checkpoints/checkpoints-DCN'

modelCheckpoint = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor='val_loss',
    mode='min',
    save_best_only=True) # Saving best checkpoint

earlyStop = tf.keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10) # stopping training when val_loss doesn't decrease in 15 epochs


model = DCN(
    feature_dict=feature_dict,
    use_cross_layer=True,
    n_cross_layers=1,
    deep_layer_size=[64,64,128],
    vocabularies=vocabularies
)

model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

model.fit(
    cached_train, 
    epochs=30,
    validation_data=cached_val,
    callbacks=[tensorboard_callback, modelCheckpoint, earlyStop])

model.load_weights(checkpoint_filepath)
model.evaluate(cached_test)

# mat = model._cross_layer._dense.kernel
# features = model._all_features

# block_norm = np.ones([len(features), len(features)])
# dim = model.embedding_dimension

# # Compute the norms of the blocks.
# for i in range(len(features)):
#   for j in range(len(features)):
#     block = mat[i * dim:(i + 1) * dim,
#                 j * dim:(j + 1) * dim]
#     block_norm[i,j] = np.linalg.norm(block, ord="fro")

# plt.figure(figsize=(9,9))
# im = plt.matshow(block_norm, cmap=plt.cm.Blues)
# ax = plt.gca()
# divider = make_axes_locatable(plt.gca())
# cax = divider.append_axes("right", size="5%", pad=0.05)
# plt.colorbar(im, cax=cax)
# cax.tick_params(labelsize=10) 
# _ = ax.set_xticklabels([""] + features, rotation=45, ha="left", fontsize=10)
# _ = ax.set_yticklabels([""] + features, fontsize=10)
# plt.savefig('cross2.png')

tf.saved_model.save(model, 'tfserving/models/DCN/{}'.format(int(time.time())))