#!/bin/bash

# Usage:
#
#  ./claude-qwen3pt8_27b                 # enter claude code
#  ./claude-qwen3pt8_27b -p "say hello"  # headless mode

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:30214 ANTHROPIC_API_KEY="" claude --model qwen3.8:27b "$@"
