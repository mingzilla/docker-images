#!/bin/bash
cd "$(dirname "$0")/.."

echo "========================================"
echo "  Claude Code Verification: gemma4:e4b"
echo "========================================"
echo ""
echo "Once inside Claude Code, paste the contents of:"
echo "  1. _verification/gemma4_e4b__1_basic.md     (12 basic capability tests)"
echo "  2. _verification/gemma4_e4b__2_agentic.md   (6 multi-step reasoning tests)"
echo ""
echo "Starting Claude Code..."
echo ""

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL="http://localhost:40204" ANTHROPIC_API_KEY="" \
    claude --model "gemma4:e4b" --dangerously-skip-permissions
