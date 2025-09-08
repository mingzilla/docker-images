#!/bin/bash

# Build custom Ollama image with pre-installed models
echo "Building custom Ollama image with pre-installed models..."
docker builder prune -f
docker build -t mingzilla/ollama-embeddinggemma:1.0.0 -t mingzilla/ollama-embeddinggemma:latest -f Dockerfile .

echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "./_publish-docker.sh 1.0.0"