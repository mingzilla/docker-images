#!/bin/bash
cd "$(dirname "$0")"
set -e

SERVICE="$1"

if [ -z "$SERVICE" ]; then
    echo "Usage: ./start.sh [e4b|26b|all]"
    exit 1
fi

case "$SERVICE" in
    e4b) PORT=40204; SERVICES="ollama-e4b" ;;
    26b) PORT=40205; SERVICES="ollama-26b" ;;
    all) SERVICES="ollama-e4b ollama-26b" ;;
    *)   echo "Unknown service: $SERVICE (use e4b, 26b, or all)"; exit 1 ;;
esac

echo "Starting $SERVICES..."
docker compose up -d $SERVICES

if [ "$SERVICE" = "all" ]; then
    echo "Waiting for ollama-e4b..."
    until curl -sf http://localhost:40204/api/version > /dev/null 2>&1; do sleep 2; done
    echo "Waiting for ollama-26b..."
    until curl -sf http://localhost:40205/api/version > /dev/null 2>&1; do sleep 2; done
else
    echo "Waiting for ollama to be ready on port $PORT..."
    until curl -sf http://localhost:$PORT/api/version > /dev/null 2>&1; do sleep 2; done
fi

echo "Ready."
docker compose ps
