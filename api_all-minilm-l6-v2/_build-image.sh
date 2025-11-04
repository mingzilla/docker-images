#!/bin/bash

echo "Building custom all-MiniLM-L6-v2 embedding API image..."
docker builder prune -f
docker build -t mingzilla/api_all-minilm-l6-v2:1.0.5 -t mingzilla/api_all-minilm-l6-v2:latest -f Dockerfile .

echo "Build completed."
echo ""
echo "To push this image to Docker Hub, run:"
echo "./_publish-docker.sh 1.0.5"