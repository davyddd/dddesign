# Local development always runs on the newest supported Python (latest patch release)
FROM python:3.14-slim

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV PYTHONBREAKPOINT=ipdb.set_trace

COPY --from=ghcr.io/astral-sh/uv:0.12.1 /uv /uvx /usr/local/bin/

RUN mkdir -p /src && \
    apt-get update && \
    apt-get install -y git gcc python3-dev libffi-dev make

WORKDIR /src

COPY pyproject.toml uv.lock /src/
RUN uv sync --frozen --all-groups --no-install-project

COPY . /src
RUN uv sync --frozen --all-groups
