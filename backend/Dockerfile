FROM python:3.12.4-slim

WORKDIR /app

# System deps some embedding libs need
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway injects $PORT at runtime — don't hardcode 8000
CMD uvicorn main:app --host 0.0.0.0 --port $PORT