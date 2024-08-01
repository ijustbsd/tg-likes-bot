FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade poetry && \
    poetry install

COPY . .

CMD ["python", "-V"]
