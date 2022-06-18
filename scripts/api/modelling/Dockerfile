FROM python:3.8

RUN apt-get update && apt-get install -y \
    cron


WORKDIR /usr/local/src/scripts/
COPY requirements.txt ./requirements.txt
COPY train_model.py ./train_model.py
COPY DCN.py ./DCN.py
RUN pip --no-cache-dir install  -r requirements.txt

COPY ./run_model_train /etc/cron.d/run_model_train
RUN chmod 0644 /etc/cron.d/run_model_train
RUN crontab /etc/cron.d/run_model_train 
RUN touch /var/log/cron.log 

CMD cron && tail -f /var/log/cron.log