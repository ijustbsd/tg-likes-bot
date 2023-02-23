FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --ignore-installed -r requirements.txt

COPY . .

CMD ["python", "-V"]
