#!/bin/bash
cd "$(dirname "$0")"
set -e

echo "Stopping ollama-qwen3pt5_9b (volumes preserved)..."
docker compose down
docker compose ps
