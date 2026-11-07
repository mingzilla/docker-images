#!/bin/bash
set -e

function ollama::rm() {
    local model_name="$1"
    echo "🗑️  Removing model: $model_name"
    docker-compose exec ollama ollama rm "$model_name" 2>/dev/null || \
    curl -X DELETE http://localhost:11434/api/delete \
      -d "{\"name\": \"$model_name\"}"
}

# Usage
ollama::rm "qwen2.5:32b"