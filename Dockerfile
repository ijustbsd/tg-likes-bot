FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN \
    apt update && \
    apt install -y gcc && \
    apt clean

COPY pyproject.toml poetry.lock ./

RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade poetry && \
    poetry install

COPY . .

CMD ["python", "-V"]
