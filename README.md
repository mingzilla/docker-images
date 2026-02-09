# Docker Images

## AI API Services

| Service                 | Type                    | Capability | Description                                 | Dimensions | Note                                                          |
|-------------------------|-------------------------|------------|---------------------------------------------|------------|---------------------------------------------------------------|
| api_all-minilm-l6-v2    | Embedding               | CPU or GPU | Official HuggingFace model all-MiniLM-L6-v2 | 384        | Uses cuda/gpu by default, falls back to cpu                   |
| ollama-all-minilm-l6-v2 | Embedding               | CPU or GPU | Official HuggingFace model all-MiniLM-L6-v2 | 384        | With GPU usage, it seems to be slower than the python version |
| ollama-nomic-embed      | Embedding               | CPU or GPU | Official nomic-embed-text                   | 768        |                                                               |
| ollama-embeddinggemma   | Embedding               | CPU or GPU | Official ollama-embeddinggemma              | 128,768    |                                                               |
| ollama-nomic-llama3     | Embedding + Completions | CPU or GPU | Official nomic-embed-text, llama3.2:3b      |            |                                                               |
| ollama-llama3           | Completions             | CPU or GPU | Official llama3.2:3b                        |            |                                                               |

Refer to [embedding-model-selection.md](_docs/embedding-model-selection.md) for embedding model selection.

## vllm models

| Feature                              | llama3.2  | qwen2.5   | qwen3     |
  |--------------------------------------|-----------|-----------|-----------|
| vLLM version                         | v0.15.1 ✅ | v0.15.1 ✅ | v0.15.1 ✅ |
| Blackwell support                    | sm_120 ✅  | sm_120 ✅  | sm_120 ✅  |
| MAX_MODEL_LEN configurable           | ✅         | ✅         | ✅         |
| VLLM_FLASH_ATTN_VERSION configurable | ✅         | ✅         | ✅         |
| Build from source                    | ✅         | ✅         | ✅         |
| Save to tar support                  | ✅         | ✅         | ✅         |

## Upgrade Ollama

1. Dockerfile

Find and replace version

2. _build-image.sh

Find and replace version number to build in each of these files.
Each project has a different number. This affects:

- _build-image.sh
- docker-compose.yml

3. _publish-docker.sh

Run this.

4. global find and replace all the docker images.

- mingzilla/ollama-llama3:1.0.0 -> mingzilla/ollama-llama3:1.0.1
- mingzilla/ollama-nomic-embed:1.0.2 -> mingzilla/ollama-nomic-embed:1.0.3
- mingzilla/ollama-nomic-llama3:1.0.0 -> mingzilla/ollama-nomic-llama3:1.0.1
