#!/bin/bash
cd "$(dirname "$0")"
set -e

PORT=40221

function docker::check_container_running() {
  if ! curl -sf http://localhost:$PORT/api/version > /dev/null 2>&1; then
      echo "Error: Ollama is not running on port $PORT. Start it first:"
      echo "  docker compose up -d"
      exit 1
  fi
}

docker::check_container_running

START=$(date +%s)

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" claude -p "say hello" --model qwen3.5

END=$(date +%s)
echo ""
echo "==> Completed in $((END - START))s"
