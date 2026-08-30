#!/bin/bash
set -e

echo "🛑 Stopping and removing containers..."
docker-compose down   # no -v: keeps the model volume (~18GB)

echo "⬆️  Refreshing Ollama image (:latest is cached otherwise)..."
docker-compose pull

echo "🚀 Starting..."
docker-compose up -d

echo "⏳ Waiting for Ollama to be ready..."
until curl -sf http://localhost:30214/api/version >/dev/null; do sleep 2; done

echo "⬇️  Pulling model (skipped if already present)..."
docker-compose exec ollama sh -c 'ollama pull "$OLLAMA_MODEL"'

echo "📊 Checking status..."
docker-compose ps
