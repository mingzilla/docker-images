### Stateless Model - Value Mapping

Note: for llm friendly create a fixed value table like the below:

| Service Type | Service                                    | DEV Port | PROD Port |
|--------------|--------------------------------------------|----------|-----------|
| Embedding    | mingzilla/api_all-minilm-l6-v2:1.0.1       | 30101    | 40101     |
| Embedding    | mingzilla/ollama-nomic-embed:1.0.3         | 30102    | 40102     |
| Embedding    | mingzilla/ollama-embeddinggemma:1.0.0      | 30103    | 40103     |
| Completions  | For Testing                                | 30200    | -         |
| Completions  | mingzilla/ollama-llama3:1.0.1              | 30201    | 40201     |
| Completions  | Qwen2.5-1.5B-Instruct                      | 30202    | 40202     |
| Completions  | google/gemma-2-2b-it                       | 30203    | 40203     |
| Completions  | google/gemma4                              | 30204    | 40204     |
| Completions  | vllm neuralmagic/Llama-3.2-3B-Instruct-FP4 | 30211    | 40211     |
| Completions  | vllm Qwen2.5-32B-Instruct-NVFP4            | 30212    | 40212     |
| Completions  | vllm nvidia/Qwen3-32B-NVFP4                | 30213    | 40213     |
| Completions  | ollama claude code                         | 30221    | 40221     |
| Reranking    |                                            | 30301    | 40301     |
