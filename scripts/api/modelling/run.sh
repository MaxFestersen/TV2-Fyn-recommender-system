docker build -t model_trainer .

docker run -it -d --rm --name model_trainer \
-v "$(pwd)/../tfserving/models/DCN/:/usr/local/src/scripts/tfserving/models/DCN/" \
-v "$(pwd)/../utility/:/usr/local/src/scripts/utility/" \
-v "$(pwd)/../secrets/.env:/usr/local/src/scripts/utility/.env" \
--network=recommender \
model_trainer

