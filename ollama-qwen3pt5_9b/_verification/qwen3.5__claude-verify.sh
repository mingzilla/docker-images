#!/bin/bash
cd "$(dirname "$0")/.."

echo "========================================"
echo "  Claude Code Verification: qwen3.5"
echo "========================================"
echo ""
echo "Once inside Claude Code, paste the contents of:"
echo "  1. _verification/qwen3.5__1_basic.md     (12 basic capability tests)"
echo "  2. _verification/qwen3.5__2_agentic.md   (6 multi-step reasoning tests)"
echo ""
echo "Starting Claude Code..."
echo ""

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL="http://localhost:40221" ANTHROPIC_API_KEY="" \
    claude --model "qwen3.5" --dangerously-skip-permissions
