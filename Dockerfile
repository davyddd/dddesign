FROM python:3.10.4-slim

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN mkdir -p /src && \
    apt-get update && \
    apt-get install -y git libpq-dev gcc python3-dev libffi-dev musl-dev make libevent-dev && \
    pip install poetry==1.5.0

RUN poetry config virtualenvs.create false

WORKDIR /src

COPY ./poetry.lock ./pyproject.toml /src/

RUN poetry install

COPY . /src