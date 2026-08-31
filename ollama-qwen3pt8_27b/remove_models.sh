#!/bin/bash
set -e

function ollama::rm() {
    local model_name="$1"
    echo "🗑️  Removing model: $model_name"
    docker compose exec ollama ollama rm "$model_name" 2>/dev/null || \
    curl -X DELETE http://localhost:30214/api/delete \
      -d "{\"name\": \"$model_name\"}"
}

# Usage
MODEL=$(docker compose exec -T ollama sh -c 'printf %s "$OLLAMA_MODEL"')
ollama::rm "$MODEL"