#!/bin/bash
cd "$(dirname "$0")/.."

echo "========================================"
echo "  Claude Code Verification: gemma4:26b"
echo "========================================"
echo ""
echo "Once inside Claude Code, paste the contents of:"
echo "  1. _verification/gemma4_26b__1_basic.md     (12 basic capability tests)"
echo "  2. _verification/gemma4_26b__2_agentic.md   (6 multi-step reasoning tests)"
echo ""
echo "Starting Claude Code..."
echo ""

ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL="http://localhost:40205" ANTHROPIC_API_KEY="" \
    claude --model "gemma4:26b" --dangerously-skip-permissions
