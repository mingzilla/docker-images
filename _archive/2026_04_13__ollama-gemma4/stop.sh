#!/bin/bash
cd "$(dirname "$0")"
set -e

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Usage: ./stop.sh [e4b|26b|all]"
    exit 1
fi

case "$SERVICE" in
    e4b) SERVICES="ollama-e4b" ;;
    26b) SERVICES="ollama-26b" ;;
    all) SERVICES="" ;;
    *)   echo "Unknown service: $SERVICE (use e4b, 26b, or all)"; exit 1 ;;
esac

if [ "$SERVICE" = "all" ]; then
    echo "Stopping all services (volumes preserved)..."
    docker compose down
else
    echo "Stopping $SERVICES (volumes preserved)..."
    docker compose stop $SERVICES
    docker compose rm -f $SERVICES
fi

docker compose ps
