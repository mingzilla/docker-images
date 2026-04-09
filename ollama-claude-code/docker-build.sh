#!/bin/bash
cd "$(dirname "$0")"
set -e

IMAGE_NAME="mingzilla/ollama-claude-code:1.0.0"
CONTAINER_NAME="ollama-claude-code-dev"
MODEL="qwen3.5"

echo "==> Starting dev container..."
docker compose -f docker-compose.dev.yml up -d

echo "==> Waiting for ollama to be ready..."
until curl -sf http://localhost:40221/api/version > /dev/null 2>&1; do
    sleep 2
    echo "    waiting..."
done
echo "==> Ollama is ready."

echo "==> Pulling model: $MODEL"
docker exec "$CONTAINER_NAME" ollama pull "$MODEL"

echo "==> Copying model from volume into container filesystem..."
docker exec "$CONTAINER_NAME" cp -r /root/.ollama /root/.ollama-baked
docker exec "$CONTAINER_NAME" rm -rf /root/.ollama
docker exec "$CONTAINER_NAME" mv /root/.ollama-baked /root/.ollama

echo "==> Stopping container..."
docker compose -f docker-compose.dev.yml stop

echo "==> Committing container as $IMAGE_NAME"
docker commit "$CONTAINER_NAME" "$IMAGE_NAME"

echo "==> Cleaning up dev container..."
docker compose -f docker-compose.dev.yml down

echo "==> Done. Image ready: $IMAGE_NAME"
echo "    Test with: ./docker-test-dev.sh"
