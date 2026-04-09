#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
URL="$1"

if [ -z "$URL" ]; then
    echo "Usage: web_fetch.sh \"https://example.com\""
    exit 1
fi

HTML=$(curl -sL "$URL")

python3 "$SCRIPT_DIR/text_cleaner.py" <<< "$HTML"
