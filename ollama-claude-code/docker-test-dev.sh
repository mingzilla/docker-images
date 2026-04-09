#!/bin/bash
cd "$(dirname "$0")"
set -e

IMAGE_NAME="mingzilla/ollama-claude-code:1.0.0"
CONTAINER_NAME="ollama-claude-code-test"
PORT=40221

echo "==> Starting test container from $IMAGE_NAME"
docker run -d --rm \
    --name "$CONTAINER_NAME" \
    --gpus all \
    -p "$PORT:11434" \
    -e OLLAMA_HOST=0.0.0.0 \
    -e OLLAMA_CONTEXT_LENGTH=65536 \
    "$IMAGE_NAME"

echo "==> Waiting for ollama to be ready..."
until curl -sf http://localhost:$PORT/api/version > /dev/null 2>&1; do
    sleep 2
    echo "    waiting..."
done
echo "==> Ollama is ready on port $PORT"

echo "==> Running test: claude -p \"say hello\""
ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:$PORT ANTHROPIC_API_KEY="" \
    claude -p "say hello" --model qwen3.5

echo ""
echo "==> Stopping test container..."
docker stop "$CONTAINER_NAME"
echo "==> Done."
