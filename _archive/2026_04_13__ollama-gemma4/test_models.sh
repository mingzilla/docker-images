#!/bin/bash
cd "$(dirname "$0")"
set -e

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Usage: ./test_models.sh [e4b|26b|all]"
    exit 1
fi

function curl::test_model() {
    local model_name="$1" port="$2"
    echo "============================== $model_name (port $port) ===================================="

    curl -X POST http://localhost:$port/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg model "$model_name" '{
        model: $model,
        messages: [{role: "user", content: "hi"}],
        stream: false
    }')" | jq .
    echo ""
}

case "$SERVICE" in
    e4b) curl::test_model "gemma4:e4b" 40204 ;;
    26b) curl::test_model "gemma4:26b" 40205 ;;
    all)
        curl::test_model "gemma4:e4b" 40204
        curl::test_model "gemma4:26b" 40205
        ;;
    *)  echo "Unknown service: $SERVICE (use e4b, 26b, or all)"; exit 1 ;;
esac
