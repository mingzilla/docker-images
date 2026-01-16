```shell
curl -X POST http://localhost:30201/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "llama3.2:3b",
        "messages": [
          {
            "role": "user",
            "content": "hi"
          }
        ],
        "stream": false
      }'
```