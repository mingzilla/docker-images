#!/bin/bash
cd "$(dirname "$0")"
set -e

function curl::test_model() {
    local model_name="$1"
    echo "============================== $model_name ===================================="

    curl -X POST http://localhost:40221/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg model "$model_name" '{
        model: $model,
        messages: [{role: "user", content: "hi"}],
        stream: false
    }')" | jq .
    echo ""
}

curl::test_model "qwen3.5"
