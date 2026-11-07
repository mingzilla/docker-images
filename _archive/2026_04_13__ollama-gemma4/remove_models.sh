#!/bin/bash
cd "$(dirname "$0")"
set -e

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Usage: ./remove_models.sh [e4b|26b|all]"
    exit 1
fi

function ollama::rm() {
    local svc="$1" model="$2" port="$3"
    echo "Removing model: $model from $svc"
    docker compose exec $svc ollama rm "$model" 2>/dev/null || \
    curl -X DELETE http://localhost:$port/api/delete \
      -d "{\"name\": \"$model\"}"
}

case "$SERVICE" in
    e4b) ollama::rm ollama-e4b "gemma4:e4b" 40204 ;;
    26b) ollama::rm ollama-26b "gemma4:26b" 40205 ;;
    all)
        ollama::rm ollama-e4b "gemma4:e4b" 40204
        ollama::rm ollama-26b "gemma4:26b" 40205
        ;;
    *)  echo "Unknown service: $SERVICE (use e4b, 26b, or all)"; exit 1 ;;
esac
