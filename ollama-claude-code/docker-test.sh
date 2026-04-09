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

./claude-qwen.sh -p "say hello"

END=$(date +%s)
echo ""
echo "==> Completed in $((END - START))s"
