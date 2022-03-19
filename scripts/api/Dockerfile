FROM python:3.8

WORKDIR /app
COPY *.py /app/
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env
RUN pip --no-cache-dir install  -r requirements.txt

CMD ["python", "./app.py"]
