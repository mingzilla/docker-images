## OpenAI-Compatible Endpoints (Primary)

### Single Text Embedding
```bash
curl -X POST http://localhost:30101/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-minilm:l6-v2",
        "input": "Hello, world!"
      }'
```

## Ollama Specific Endpoints

### Single Text Embedding
```bash
curl -X POST http://localhost:30101/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-minilm:l6-v2",
        "input": "Hello, world!"
      }'
```
