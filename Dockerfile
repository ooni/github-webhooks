FROM python:3.7.5-alpine

RUN apk update && apk add libressl-dev postgresql-dev libffi-dev gcc musl-dev python3-dev
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python ./main.py
