FROM python:3.12.6-slim

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir -p /src && \
    apt-get update && \
    apt-get install -y git libpq-dev gcc python3-dev libffi-dev musl-dev make libevent-dev && \
    pip install poetry==1.8.3

RUN poetry config virtualenvs.create false

WORKDIR /src

COPY . /src
RUN poetry install