# ollama-qwen3pt5_9b

Ollama container running Alibaba's Qwen 3.5 9B model on port **40221**.

## Model Specs

| Spec           | Value       |
|----------------|-------------|
| Parameters     | 9B (q4_K_M) |
| Context window | 128K tokens |
| Download size  | 6.6GB       |
| VRAM (64K ctx) | ~16.6GB     |

https://www.canirun.ai/device/rtx-5090-laptop?q=qwen+3.5

| Model Name         | License    | Ago     | Size     | RAM % | Context  | Speed      | Performance | Score  |
|:-------------------|:-----------|:--------|:---------|:------|:---------|:-----------|:------------|:-------|
| Qwen 3.5 9B        | Apache 2.0 | 2mo ago | 5.1 GB   | 21%   | 32K ctx  | ~123 tok/s | Runs great  | 96/100 |
| Qwen 3.5 4B        | Apache 2.0 | 2mo ago | 2.5 GB   | 10%   | 32K ctx  | ~251 tok/s | Runs great  | 95/100 |
| Qwen 3.5 2B        | Apache 2.0 | 2mo ago | 1.5 GB   | 6%    | 32K ctx  | ~418 tok/s | Runs great  | 93/100 |
| Qwen 3.5 0.8B      | Apache 2.0 | 2mo ago | 0.9 GB   | 4%    | 32K ctx  | ~697 tok/s | Runs great  | 92/100 |
| Qwen 3.5 27B       | Apache 2.0 | 2mo ago | 14.7 GB  | 61%   | 256K ctx | ~43 tok/s  | Runs well   | 70/100 |
| Qwen 3.5 35B-A3B   | Apache 2.0 | 2mo ago | 18.4 GB  | 77%   | 256K ctx | ~34 tok/s  | Decent      | 59/100 |
| Qwen 3.5 122B-A10B | Apache 2.0 | 2mo ago | 63 GB    | 263%  | 256K ctx | 0 tok/s    | Too heavy   | 0/100  |
| Qwen 3.5 397B-A17B | Apache 2.0 | 2mo ago | 203.9 GB | 850%  | 256K ctx | 0 tok/s    | Too heavy   | 0/100  |

## Usage

Named volume persists model across restarts.

```bash
# Start container
./start.sh

# Pull model (first time only, requires container running)
./pull.sh

# Test inference
./test_models.sh

# Stop (model preserved)
./stop.sh

# Remove model weights from volume
./remove_models.sh

# Nuclear: wipe container + volume
./clean.sh
```
