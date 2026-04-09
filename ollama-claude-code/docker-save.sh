#!/bin/bash
cd "$(dirname "$0")"
set -e

IMAGE_NAME="mingzilla/ollama-claude-code:1.0.0"
OUTPUT_FILE="mingzilla__ollama-claude-code__1.0.0.tar"

echo "==> Saving $IMAGE_NAME to $OUTPUT_FILE"
docker save -o "$OUTPUT_FILE" "$IMAGE_NAME"

echo "==> Done. Saved: $OUTPUT_FILE ($(du -h "$OUTPUT_FILE" | cut -f1))"
echo "    Load with: docker load -i $OUTPUT_FILE"
