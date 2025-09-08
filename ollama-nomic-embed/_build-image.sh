#!/bin/bash

# Build custom Ollama image with pre-installed models
echo "Building custom Ollama image with pre-installed models..."
docker builder prune -f
docker build -t mingzilla/ollama-nomic-embed:1.0.3 -t mingzilla/ollama-nomic-embed:latest -f Dockerfile .

echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "./_publish-docker.sh 1.0.3"