FROM python:3.8

WORKDIR /app
COPY app.py requirements.txt /app/
COPY utility /app/utility
RUN pip --no-cache-dir install  -r requirements.txt

EXPOSE 8080

CMD ["python", "./app.py"]
