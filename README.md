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

## vllm nvpf4 models

### How LLM Processing works

- Prefill: Processes the full input prompt in parallel, compute-intensive, high GPU utilization
- Decode: Autoregressive token generation, memory bandwidth-bound, lower GPU utilization

```text
Prefill:  ████████████████████  Compute-bound (matmuls, FLOPs maxed)
          GPU: ~100% utilization
          "Using all the CUDA cores"

Decode:   ░░░░░░░░░░░░░░░░░░░░  Memory bandwidth-bound
          GPU: ~10-30% utilization  
          "Waiting on VRAM → cache transfers, compute idle"


 Prefill     Decode
 [AAAAAA] -> [AA    ]
                |  |
                BB |
                   CC
```

```text
Prefill:  [A] → [B] → [C]  (sequential, even with NVFP4)
Decode:   [A1+B1] → [A2+B2] → [A3+B3]  (batched together)
```

### How NVFP4 works

- Each bit is 0 or 1
- FP4 means: each value has 4 bits
- FP16 means: each value has 16 bits
- so for the same size of data transition e.g. 16mb, assuming it 64 bits bus bandwidth, fp4 has a shorter queue to move the data through than fp16 then

| Format  | Bits per Value | Example Value    | Values in 16MB | "Queue Length" for Same Compute |
|---------|----------------|------------------|----------------|---------------------------------|
| FP16    | 16             | 0001000100010001 | 8 million      | Longer queue                    |
| FP8     | 8              | 00010001         | 16 million     | Medium queue                    |
| **FP4** | **4**          | 0001             | **32 million** | **Shorter queue**               |

```text
FP16:  [VRAM] ======== 16MB ========> [Tensor Cores]  (wait...)
       8M values @ 16-bit each

FP4:   [VRAM] ==== 4MB ====> [Tensor Cores]  (done, next!)
       8M values @ 4-bit each
```

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
