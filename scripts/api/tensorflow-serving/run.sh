#!/bin/bash
docker run -p 8501:8501 -t --rm -d --name DCN -v "$(pwd)/models/DCN:/models/DCN" -e MODEL_NAME=DCN tensorflow/serving:2.8.0
