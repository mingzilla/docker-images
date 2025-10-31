# API all-MiniLM-L6-v2 Embedding Service

A CPU-only Docker container providing OpenAI-compatible embedding API using the [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model.

## Overview

This project creates a Docker image that:

- **Uses CPU-only processing** - No GPU dependencies, avoiding the 8GB+ image sizes and compatibility issues of GPU-based solutions
- **Pre-embeds the model** - The all-MiniLM-L6-v2 model is downloaded during Docker build, not at runtime
- **Provides instant startup** - No model downloads or volumes required when starting containers
- **Offers dual API compatibility** - Both OpenAI and Ollama endpoint formats supported
- **Runs on FastAPI** - Minimal overhead compared to LLM resource usage, perfect for HTTP-based embedding requests

## Features

- 🚀 **Instant startup** - Model pre-downloaded in Docker image
- 🔄 **OpenAI Compatible** - Drop-in replacement for OpenAI embedding API
- 🦙 **Ollama Compatible** - Secondary endpoint matching Ollama's format
- 💻 **CPU Only** - No GPU requirements, runs anywhere
- 🐳 **Docker First** - Self-contained with no external dependencies
- ⚡ **FastAPI** - High-performance async API framework
- 📏 **384 dimensions** - Compact yet effective embeddings

## Technical Specifications

- **Base Image**: `python:3.11-slim`
- **Framework**: FastAPI + uvicorn
- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Internal Port**: 8000
- **External Port**: 30101 (via docker-compose)
- **Container Name**: `api_all-minilm-l6-v2`
- **Image Name**: `mingzilla/api_all-minilm-l6-v2`

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Start the service
docker-compose up -d

# Check health
curl http://localhost:30101/health

# Test embedding
curl -X POST http://localhost:30101/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "all-MiniLM-L6-v2", "input": "Hello, world!"}'
```

### Using Docker Run

```bash
# Run container directly
docker run -d \
  --name api_all-minilm-l6-v2 \
  -p 30101:8000 \
  mingzilla/api_all-minilm-l6-v2:latest

# Test the service
curl http://localhost:30101/health
```

## API Endpoints

### Primary: OpenAI-Compatible

- `POST /v1/embeddings` - Generate embeddings (OpenAI format)
- `GET /v1/models` - List available models

### Secondary: Ollama-Compatible

- `POST /api/embed` - Generate embeddings (Ollama format)

### Health & Status

- `GET /health` - Service health check

For detailed API examples and response formats, see [curl.md](curl.md).

## Development

### Building from Source

```bash
# Build the Docker image
./_build-image.sh

# Publish to Docker Hub
./_publish-docker.sh 1.0.2
```

### Adapting for Other Models

To create a version with a different sentence-transformers model:

1. **Copy the directory**:
   ```bash
   cp -r api_all-minilm-l6-v2 api_all-your-model-name
   cd api_all-your-model-name
   ```

2. **Find and replace model references**:
   - In `app.py`: Update `MODEL_NAME` variable
   - In `Dockerfile`: Update the model download command
   - In `README.md` and other docs: Update model name references
   - In file/directory names as needed

3. **Update Docker image naming**:
   - In `_build-image.sh`: Update image tags
   - In `_publish-docker.sh`: Update image names
   - In `docker-compose.yml`: Update service and image names

## Architecture Decisions

### Why CPU-Only?

- **Smaller images**: CPU-only PyTorch is ~200MB vs 8GB+ for GPU variants
- **Better compatibility**: Works on any machine without GPU driver requirements
- **Simpler deployment**: No CUDA version matching or GPU resource allocation
- **Cost effective**: Can run on cheaper CPU-only cloud instances

### Why FastAPI?

- **Minimal overhead**: HTTP API overhead is negligible compared to LLM inference costs
- **Project isolation**: Avoids Python dependency conflicts in larger projects
- **Scalability**: Easy to scale horizontally with multiple containers
- **Standards compliance**: OpenAI-compatible endpoints for ecosystem integration

### Why Pre-Downloaded Models?

- **Instant startup**: No waiting for model downloads when scaling containers
- **No volumes needed**: Self-contained images with no external storage requirements
- **Reliable deployment**: No network dependency during container startup
- **Immutable deployments**: Consistent model versions across environments

## Model Information

- **Model**: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Dimensions**: 384
- **Max Sequence Length**: 256 tokens
- **Model Size**: ~90MB
- **Performance**: Excellent balance of speed, size, and quality

## License

This project provides a Docker wrapper around the sentence-transformers library and all-MiniLM-L6-v2 model. Please refer to the respective licenses:

- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)