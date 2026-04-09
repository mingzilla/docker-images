#!/bin/bash
QUERY="$1"
NUM_RESULTS="${2:-5}"

if [ -z "$QUERY" ]; then
    echo "Usage: web_search.sh \"search query\" [num_results]"
    exit 1
fi

ddgr --np --noprompt -n "$NUM_RESULTS" "$QUERY"
