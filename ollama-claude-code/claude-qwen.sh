#!/bin/bash

# Usage:
#
#  ./claude-qwen.sh -p "say hello"

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" claude --model qwen3.5 "$@"
