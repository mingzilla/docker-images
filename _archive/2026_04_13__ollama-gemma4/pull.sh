#!/bin/bash
cd "$(dirname "$0")"
set -e

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Usage: ./pull.sh [e4b|26b|all]"
    exit 1
fi

function pull_model() {
    local svc="$1" model="$2" port="$3"
    echo "Pulling $model into $svc..."
    if ! curl -sf http://localhost:$port/api/version > /dev/null 2>&1; then
        echo "Error: $svc is not running on port $port. Run ./start.sh $4 first."
        exit 1
    fi
    docker compose exec $svc ollama pull $model
    echo "$model pulled."
}

case "$SERVICE" in
    e4b) pull_model ollama-e4b "gemma4:e4b" 40204 e4b ;;
    26b) pull_model ollama-26b "gemma4:26b" 40205 26b ;;
    all)
        pull_model ollama-e4b "gemma4:e4b" 40204 e4b
        pull_model ollama-26b "gemma4:26b" 40205 26b
        ;;
    *)  echo "Unknown service: $SERVICE (use e4b, 26b, or all)"; exit 1 ;;
esac
