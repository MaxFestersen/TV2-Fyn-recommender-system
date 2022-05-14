FROM python:3.8

WORKDIR /srv/app/
COPY requirements.txt ./requirements.txt
RUN pip --no-cache-dir install  -r requirements.txt

EXPOSE 8080

CMD ["python", "./app.py"]
