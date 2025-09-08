#!/bin/bash

# Build custom Ollama image with pre-installed models
echo "Building custom Ollama image with pre-installed models..."
docker build -t mingzilla/ollama-nomic-llama3:1.0.1 -t mingzilla/ollama-nomic-llama3:latest -f Dockerfile .

echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "./_publish-docker.sh 1.0.1"