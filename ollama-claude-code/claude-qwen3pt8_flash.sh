#!/bin/bash

# Usage:
#
#  ./ollama-qwen3pt8_flash                 # enter claude code
#  ./ollama-qwen3pt8_flash -p "say hello"  # headless mode

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:30214 ANTHROPIC_API_KEY="" claude --model qwen3.8-flash-next:125b-a6b-nvfp4 "$@"
