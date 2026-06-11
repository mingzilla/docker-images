#!/bin/bash
SCRIPT_DIR="$(dirname "$0")"
URL="$1"

if [ -z "$URL" ]; then
    echo "Usage: web_fetch.sh \"https://example.com\""
    exit 1
fi

HTML=$(curl -sL "$URL")

# clean via the cleaner's static method (n-gram pass off); always emit cleaned
# bytes even when the quality filter rejects.
python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from text_cleaner import CompanyTextCleaner; c, s = CompanyTextCleaner.clean_text_without_ngram_dedup(sys.stdin.read()); print(c if c is not None else s['cleaned_text_if_rejected'])" <<< "$HTML"
