#!/bin/bash
cd "$(dirname "$0")"
set -e

PORT=40221

if ! curl -sf http://localhost:$PORT/api/version > /dev/null 2>&1; then
    echo "Error: Ollama is not running on port $PORT. Start it first:"
    echo "  docker compose -f docker-compose.dev.yml up -d"
    exit 1
fi

START=$(date +%s)

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:$PORT ANTHROPIC_API_KEY="" \
    claude -p "say hello" --model qwen3.5

END=$(date +%s)
echo ""
echo "==> Completed in $((END - START))s"
