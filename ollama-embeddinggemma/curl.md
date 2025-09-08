```shell
curl -X POST http://localhost:30103/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
        "model": "embeddinggemma:300m",
        "prompt": "Hi"
      }'
```