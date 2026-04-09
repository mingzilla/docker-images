#!/bin/bash
cd "$(dirname "$0")"
set -e

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" \
    claude -p "say hello" --model qwen3.5
