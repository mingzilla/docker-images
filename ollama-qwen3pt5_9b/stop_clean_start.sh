#!/bin/bash
cd "$(dirname "$0")"
set -e

echo "Stopping and removing containers..."
docker compose down -v

echo "Pulling latest and starting..."
docker compose up -d

echo "Waiting for ollama to be ready..."
until curl -sf http://localhost:40221/api/version > /dev/null 2>&1; do
    sleep 2
done

docker compose exec ollama ollama pull qwen3.5

echo "Checking status..."
sleep 5
docker compose ps
