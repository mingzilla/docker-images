# API Testing Examples

## OpenAI-Compatible Endpoints (Primary)

### Single Text Embedding
```bash
curl -X POST http://localhost:30101/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-MiniLM-L6-v2",
        "input": "Hello, world!"
      }'
```

### Multiple Text Embeddings
```bash
curl -X POST http://localhost:30101/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-MiniLM-L6-v2",
        "input": ["Hello, world!", "How are you today?", "This is a test sentence."]
      }'
```

### List Available Models
```bash
curl -X GET http://localhost:30101/v1/models
```

## Ollama-Compatible Endpoint (Secondary)

### Single Text Embedding (Ollama Format)
```bash
curl -X POST http://localhost:30101/api/embed \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-MiniLM-L6-v2",
        "input": "Hello, world!"
      }'
```

### Multiple Text Embeddings (Ollama Format)
```bash
curl -X POST http://localhost:30101/api/embed \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-MiniLM-L6-v2",
        "input": ["Hello, world!", "How are you today?"]
      }'
```

## Health Check

### Check Service Health
```bash
curl -X GET http://localhost:30101/health
```

## Response Formats

### OpenAI Format Response
```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0012, -0.0023, 0.0034, ...],
      "index": 0
    }
  ],
  "model": "all-MiniLM-L6-v2",
  "usage": {
    "prompt_tokens": 3,
    "total_tokens": 3
  }
}
```

### Ollama Format Response
```json
{
  "model": "all-MiniLM-L6-v2",
  "embeddings": [
    [0.0012, -0.0023, 0.0034, ...]
  ]
}
```

## Usage Notes

- The service runs on port 8000 internally but is exposed on port 30101 via docker-compose
- Both endpoints support single strings or arrays of strings as input
- The model produces 384-dimensional embeddings
- GPU acceleration is automatically used when available
- Maximum input length is 256 tokens per the model specifications