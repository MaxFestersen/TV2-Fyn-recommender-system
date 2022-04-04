

docker run docker run -it --rm -d --name DCN -v "$(pwd)/models/DCN:/models/DCN" -e MODEL_NAME=DCN tensorflow/serving:2.8.0
