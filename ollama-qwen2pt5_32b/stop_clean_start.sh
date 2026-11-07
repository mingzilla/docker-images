#!/bin/bash
set -e

echo "🛑 Stopping and removing containers..."
docker-compose down -v

echo "🧹 Removing old Ollama image..."
docker image rm ollama/ollama:latest 2>/dev/null || echo "Image not found, continuing..."

echo "🚀 Pulling latest and starting..."

docker-compose up -d
docker-compose exec ollama ollama pull qwen2.5:32b

echo "📊 Checking status..."
sleep 5
docker-compose ps
