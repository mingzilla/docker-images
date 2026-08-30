#!/bin/bash
set -e

function curl::test_model() {
    local model_name="$1"
    echo "============================== $model_name ===================================="

    curl -X POST http://localhost:30214/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg model "$model_name" '{
        model: $model,
        messages: [{role: "user", content: "hi"}],
        stream: false
    }')" | jq .
    echo ""
}

MODEL=$(docker-compose exec -T ollama sh -c 'printf %s "$OLLAMA_MODEL"')
curl::test_model "$MODEL"