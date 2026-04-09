#!/bin/bash
set -e

echo "Installing requirements for ollama-claude-code..."
echo ""

apt-get update -qq

apt-get install -y -qq jq
echo "  jq     - parse and manipulate JSON"

echo "  duckdb - SQL analytics on local files -- check website to manual install"

apt-get install -y -qq ddgr
echo "  ddgr   - DuckDuckGo search from terminal"

echo ""
echo "Done."
