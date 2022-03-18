FROM python:3.8

WORKDIR /app
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt
COPY .env /app/.env
RUN pip --no-cache-dir install  -r requirements.txt

EXPOSE 5000

CMD ["python", "./app.py"]
