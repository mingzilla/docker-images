#!/bin/bash
cd "$(dirname "$0")"
set -e

OUTPUT_FILE="mingzilla__ollama-claude-code-qwen3pt5__1.0.0.tar"

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: $OUTPUT_FILE not found. Run ./docker-save.sh first."
    exit 1
fi

echo "==> Loading image from $OUTPUT_FILE"
docker load -i "$OUTPUT_FILE"

echo "==> Done."
