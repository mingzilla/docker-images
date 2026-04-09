#!/bin/bash
cd "$(dirname "$0")"
set -e

IMAGE_NAME="mingzilla/ollama-claude-code-qwen3pt5:1.0.0"
CONTAINER_NAME="ollama-claude-code-build"
MODEL="qwen3.5"
PORT=40221
MODELS_DIR="./docker-volumes/models"

echo "==> Starting build container (no volume)..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --gpus all \
    -p "$PORT:11434" \
    -e OLLAMA_HOST=0.0.0.0 \
    -e OLLAMA_CONTEXT_LENGTH=65536 \
    ollama/ollama:0.20.3

echo "==> Waiting for ollama to be ready..."
until curl -sf http://localhost:$PORT/api/version > /dev/null 2>&1; do
    sleep 2
    echo "    waiting..."
done
echo "==> Ollama is ready."

if [ -d "$MODELS_DIR" ]; then
    echo "==> Copying cached models into container..."
    docker cp "$MODELS_DIR/." "$CONTAINER_NAME":/root/.ollama/models
else
    echo "==> No cached models found, pulling model: $MODEL"
    docker exec "$CONTAINER_NAME" ollama pull "$MODEL"
fi

echo "==> Verifying model..."
docker exec "$CONTAINER_NAME" ollama list

echo "==> Stopping container..."
docker stop "$CONTAINER_NAME"

echo "==> Committing container as $IMAGE_NAME"
docker commit "$CONTAINER_NAME" "$IMAGE_NAME"

echo "==> Done. Image ready: $IMAGE_NAME"
echo "    Test with: docker compose up -d && ./docker-test.sh"
