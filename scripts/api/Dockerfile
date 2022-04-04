FROM python:3.8

WORKDIR /app
COPY app.py data_optimized.py .env requirements.txt SVDpp_model /app/
RUN pip --no-cache-dir install  -r requirements.txt

EXPOSE 8080

CMD ["python", "./app.py"]
