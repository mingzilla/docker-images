## OpenAI Format

```bash
curl -X POST http://localhost:30101/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-minilm:l6-v2",
        "input": "Hi"
      }'
```

## Ollama Custom Format (old - avoid)

```bash
curl -X POST http://localhost:30101/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "all-minilm:l6-v2",
        "input": "Hi"
      }'
```
