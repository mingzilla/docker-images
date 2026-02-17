## vLLM Batch Processing

- Requests: async rest API calls
- vLLM's scheduler batches requests at the engine level, not the HTTP level.

```text
Your Python client (concurrent):
┌─────────────────────────────────────┐
│ asyncio.gather(                     │
│   request_1(),  ──┐                 │
│   request_2(),  ──┼── All fired     │
│   request_3(),  ──┤   within 1-5ms  │
│   ...             │                 │
│ )                 │                 │
└───────────────────┼─────────────────┘
                    │
                    ▼
        HTTP Server (vLLM)
        ┌────────────────────────────────┐
        │ Request 1 arrives ──► Queue    │
        │ Request 2 arrives ──► Queue    │  ◄── "Batch formation window"
        │ Request 3 arrives ──► Queue    │      (default: 0-2ms)
        │ ...                            │
        │ Scheduler: "I have N requests, │
        │   batch them for GPU"          │
        └────────────────────────────────┘
                    │
                    ▼
        GPU Kernel Launch (actual batch)
        ┌─────────────────────────────┐
        │ Prefill: Process 1..N       │
        │   (parallel attention)      │
        │ Decode: Step 1 for all N    │
        │ Decode: Step 2 for all N    │
        │ ...                         │
        └─────────────────────────────┘
```

### Request Timeline:

```text
Request Timeline:
t=0ms:   Requests A,B,C,D,E,F,G,H arrive (within 10ms window)
t=10ms:  vLLM scheduler: "I have 8 requests, let's batch them!"

GPU Timeline (Continuous Batching):
[0ms-50ms]   Prefill Phase: Process A+B+C+D+E+F+G+H simultaneously (100% compute)
[50ms-100ms] Decode Step 1: Generate token 1 for all 8 sequences (batched)
[100ms-150ms] Decode Step 2: Generate token 2 for all 8 sequences (batched)
...
[10s]        All 8 requests complete

Total time: ~10 seconds for 8 requests (vs 80 seconds sequential)
```

### Do we have vRAM for Batch Processing?

vRAM is used by e.g.

- Model weights (~3B parameters × dtype size)
- KV cache (the majority of remaining memory)
- Activation memory (for intermediate computations)
- CUDA graphs & overhead

```shell
vllm-llama3dot2_3b$ docker compose up -d
vllm-llama3dot2_3b$ nvidia-smi

+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.65.05              Driver Version: 580.88         CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 5090 ...    On  |   00000000:01:00.0 Off |                  N/A |
| N/A   45C    P8              5W /  150W |   22504MiB /  24463MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A               9      C   /python3.11                           N/A      |
|    0   N/A  N/A               9      C   /python3.11                           N/A      |
|    0   N/A  N/A             283      C   /python3.12                           N/A      |
+-----------------------------------------------------------------------------------------+
```

### Plan and Preparation

```shell
vllm-llama3dot2_3b$ docker logs vllm-llama3.2-nvfp4 2>&1 | grep -E "(Loading model|weights|KV cache|memory)"
(APIServer pid=1) WARNING 02-12 11:21:05 [interface.py:470] Using 'pin_memory=False' as WSL is detected. This may slow down the performance.
(EngineCore_DP0 pid=283) WARNING 02-12 11:21:11 [interface.py:470] Using 'pin_memory=False' as WSL is detected. This may slow down the performance.
(EngineCore_DP0 pid=283) INFO 02-12 11:21:28 [default_loader.py:291] Loading weights took 2.45 seconds
(EngineCore_DP0 pid=283) INFO 02-12 11:21:29 [gpu_model_runner.py:4130] Model loading took 2.26 GiB memory and 16.657731 seconds
(EngineCore_DP0 pid=283) INFO 02-12 11:21:43 [gpu_worker.py:356] Available KV cache memory: 18.03 GiB
(EngineCore_DP0 pid=283) INFO 02-12 11:21:43 [kv_cache_utils.py:1307] GPU KV cache size: 168,832 tokens
```

This means: Max batch_size=20, Safe batch_size=16 (This machine **physically cannot exceed 20 concurrent 8k sequences**)

| Metric                         | Value       |
|--------------------------------|-------------|
| Total KV Cache Memory          | 18.03 GiB   |
| Total KV Cache Tokens          | 168,832     |
| Tokens per Request (your max)  | 8,192       |
| **Max Concurrent 8k Requests** | **20**      |
| Remaining Tokens (unused)      | 4,992 (~5k) |

### Execution

#### Logs

```shell
vllm-llama3dot2_3b$ docker logs vllm-llama3.2-nvfp4 2>&1 | grep -E "(Loading model|weights|KV cache|memory)"

(APIServer pid=1) INFO 02-12 14:27:01 [loggers.py:257] Engine 000: Avg prompt throughput: 7107.0 tokens/s, Avg generation throughput: 520.0 tokens/s, Running: 9 reqs, Waiting: 6 reqs, GPU KV cache usage: 13.3%, Prefix cache hit rate: 5.2%
(APIServer pid=1) INFO 02-12 14:27:11 [loggers.py:257] Engine 000: Avg prompt throughput: 7467.3 tokens/s, Avg generation throughput: 603.7 tokens/s, Running: 14 reqs, Waiting: 0 reqs, GPU KV cache usage: 28.8%, Prefix cache hit rate: 5.7%
(APIServer pid=1) INFO 02-12 14:27:21 [loggers.py:257] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 480.7 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.8%, Prefix cache hit rate: 5.7%
(APIServer pid=1) INFO 02-12 14:27:31 [loggers.py:257] Engine 000: Avg prompt throughput: 4110.1 tokens/s, Avg generation throughput: 174.8 tokens/s, Running: 13 reqs, Waiting: 0 reqs, GPU KV cache usage: 24.7%, Prefix cache hit rate: 6.1%
(APIServer pid=1) INFO 02-12 14:27:41 [loggers.py:257] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 414.1 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 2.9%, Prefix cache hit rate: 6.1%
```

#### Log Analysis

| Time     | Running | Waiting | KV Cache Used | What's Happening                                          |
|----------|---------|---------|---------------|-----------------------------------------------------------|
| 14:27:01 | **9**   | **6**   | 13.3%         | **Prefill phase** - Processing 9 prompts, 6 queued        |
| 14:27:11 | **14**  | **0**   | 28.8%         | **Full batch** - All 15 requests now running (9+6 merged) |
| 14:27:21 | **1**   | **0**   | 2.8%          | **Cleanup** - 14 requests finished, 1 still generating    |
| 14:27:31 | **13**  | **0**   | 24.7%         | **New wave** - 13 new requests batched                    |
| 14:27:41 | **1**   | **0**   | 2.9%          | **Finishing** - Almost done                               |

#### Throughput Pattern

| Phase                  | Prompt Throughput | Generation Throughput |
|------------------------|-------------------|-----------------------|
| Prefill (14:27:01)     | 7,107 t/s         | 520 t/s               |
| Mixed (14:27:11)       | 7,467 t/s         | 604 t/s               |
| Decode-only (14:27:21) | 0 t/s             | 481 t/s               |

## NVPF4 models

(Blackwell 4-bit floating point)

### How NVPF4 works

- Prefill: Processes the full input prompt in parallel, compute-intensive, high GPU utilization
- Decode: Autoregressive token generation, memory bandwidth-bound, lower GPU utilization

```text
Prefill:  [A] → [B] → [C]  (sequential, compute-bound, NVFP4 helps little)
Decode:   [A1+B1+C1...]    (batched, bandwidth-bound, NVFP4 helps massively)
          ↑
          4× more tokens per memory fetch


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
