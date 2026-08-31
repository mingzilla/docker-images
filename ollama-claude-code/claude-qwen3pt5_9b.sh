#!/bin/bash

# Usage:
#
#  ./claude-qwen3pt5_9b                 # enter claude code
#  ./claude-qwen3pt5_9b -p "say hello"  # headless mode

# CLAUDE_CODE_ATTRIBUTION_HEADER=0 — keeps the system-prompt prefix stable so
# Ollama reuses the cached KV prefix on repeated turns. Without it, Claude Code
# prepends a per-conversation attribution block that shifts the prefix every
# turn, forcing a full re-prefill of the whole context.

CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
ANTHROPIC_AUTH_TOKEN=ollama \
ANTHROPIC_BASE_URL=http://localhost:40221 \
ANTHROPIC_API_KEY="" \
claude --model qwen3.5 "$@"
