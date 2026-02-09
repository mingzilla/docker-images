#!/bin/bash
set -e

function curl::test_model() {
    local port_number="$1"
    local model_name="$2"
    echo "============================== $model_name ===================================="

    curl -X POST "http://localhost:$port_number/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$(
        jq -n \
        --arg model "$model_name" \
        '{
            model: $model,
            messages: [{role: "user", "content": "hi"}],
            stream: false,
            max_tokens: 2048
        }'
    )" | jq .
    echo ""
}

function docker::view_logs() {
    local model_name="$1"
    docker logs -f "$model_name"
}

function help::show() {
    local model_name="$1"

    echo "Usage: $0 <command>"
    echo ""
    echo "Available commands:"
    echo "  curl_$model_name      Test $model_name"
    echo "  log_$model_name       View logs for $model_name"
    echo ""
    echo "Examples:"
    echo "  $0 curl_$model_name"
    echo "  $0 log_$model_name"
}
