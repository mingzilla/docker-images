#!/bin/bash

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "Error: Version tag is required"
    echo "Usage: ./_publish-docker.sh <version>"
    echo "Example: ./_publish-docker.sh 1.0.1"
    exit 1
fi

VERSION=$1
IMAGE_NAME="mingzilla/api_all-minilm-l6-v2"

echo "Publishing $IMAGE_NAME:$VERSION to Docker Hub..."

# Verify image exists
if ! docker image inspect $IMAGE_NAME:latest >/dev/null 2>&1; then
    echo "Error: Image $IMAGE_NAME:latest not found. Run ./build-image.sh first."
    exit 1
fi

# Tag the image with version
docker tag $IMAGE_NAME:latest $IMAGE_NAME:$VERSION

# Push both tags to Docker Hub
docker push $IMAGE_NAME:$VERSION
docker push $IMAGE_NAME:latest

echo "Successfully published:"
echo "- $IMAGE_NAME:$VERSION"
echo "- $IMAGE_NAME:latest"