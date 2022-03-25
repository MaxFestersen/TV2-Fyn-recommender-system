#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import numpy as np
from data import DataTransform
from sklearn.preprocessing import minmax_scale
from recommenders.utils.python_utils import binarize
from recommenders.utils.timer import Timer
from recommenders.datasets import movielens
from recommenders.datasets.python_splitters import python_stratified_split
from recommenders.evaluation.python_evaluation import (
    map_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    rmse,
    mae,
    logloss,
    rsquared,
    exp_var
)
from recommenders.models.sar import SAR

## Following example https://github.com/microsoft/recommenders/blob/c4435a9af5836f3d472cfa44b312841a8121923c/examples/00_quick_start/sar_movielens.ipynb

data = DataTransform().computeAffinity()

train, test = python_stratified_split(data, ratio=0.75, col_user='deviceID', col_item='articleID')

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)-8s %(message)s')

model = SAR(
    col_user='deviceID',
    col_item='articleID',
    col_rating='affinity',
    col_timestamp='date',
    similarity_type='jaccard',
    time_decay_coefficient=7,
    timedecay_formula=True,
    normalize=True
)

with Timer() as train_time:
    model.fit(train)

print("Took {} seconds for training.".format(train_time.interval))

with Timer() as test_time:
    top_k = model.recommend_k_items(test, remove_seen=True)

print("Took {} seconds for prediction.".format(test_time.interval))
