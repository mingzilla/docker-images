## OpenAI Format

```shell
curl -X POST http://localhost:30102/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "nomic-embed-text",
        "input": "Hi"
      }'
```

## Ollama Custom Format (old - avoid)

```shell
curl -X POST http://localhost:11435/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "nomic-embed-text",
        "prompt": "Hi"
      }'
```
