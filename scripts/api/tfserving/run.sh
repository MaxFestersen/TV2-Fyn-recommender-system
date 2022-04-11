#!/bin/bash
docker run -it -p 8500:8500 -p 8501:8501 --rm -d --name DCN \
-v "$(pwd)/models/DCN:/models/DCN" \
-e MODEL_NAME=DCN \
--network=recommender \
tensorflow/serving:2.8.0

#tensorboard --logdir $(pwd)/tmp/tensorboard --port 6006
