FROM python:3.11-slim

ENV PYTHONPATH=/app

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade poetry && \
    poetry install

COPY . .

CMD ["python", "-V"]
