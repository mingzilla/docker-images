#!/bin/bash
cd "$(dirname "$0")"
set -e

echo "Starting ollama-qwen3pt5_9b..."
docker compose up -d

echo "Waiting for ollama to be ready on port 40221..."
until curl -sf http://localhost:40221/api/version > /dev/null 2>&1; do
    sleep 2
done

echo "Ready."
docker compose ps
