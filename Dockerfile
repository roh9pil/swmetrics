FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sma_collector ./sma_collector

# Git CLI가 필요하므로 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

CMD ["python", "-m", "sma_collector.main"]

