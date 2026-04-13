#!/bin/bash
cd "$(dirname "$0")"
set -e

if ! curl -sf http://localhost:40221/api/version > /dev/null 2>&1; then
    echo "Error: ollama is not running on port 40221. Run ./start.sh first."
    exit 1
fi

echo "Pulling qwen3.5..."
docker compose exec ollama ollama pull qwen3.5
echo "Done."
