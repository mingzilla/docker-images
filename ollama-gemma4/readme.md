# ollama-gemma4

Ollama container running Google's Gemma 4 model on port **40204**.

## Model Variants

| Variant                | Params         | VRAM needed | Context | Download |
|------------------------|----------------|-------------|---------|----------|
| `gemma4:e2b`           | 2.3B           | ~4GB        | 128K    | 7.2GB    |
| `gemma4:e4b` (default) | 4.5B effective | ~6GB        | 128K    | 9.6GB    |
| `gemma4:26b` (MoE)     | 3.8B active    | ~15-18GB    | 256K    | 18GB     |
| `gemma4:31b` (dense)   | 30.7B          | ~24GB       | 256K    | 20GB     |

Check https://www.canirun.ai/device/rtx-5090-laptop?q=gemma+4

| Model Name         | Family | Ago    | Size    | RAM % | Context  | Speed      | Performance | Score  |
|:-------------------|:-------|:-------|:--------|:------|:---------|:-----------|:------------|:-------|
| Gemma 4 E4B IT     | Gemma  | 5d ago | 4.6 GB  | 19%   | 256K ctx | ~136 tok/s | Runs great  | 96/100 |
| Gemma 4 E4B        | Gemma  | 5d ago | 4.6 GB  | 19%   | 256K ctx | ~136 tok/s | Runs great  | 96/100 |
| Gemma 4 E2B IT     | Gemma  | 5d ago | 3.1 GB  | 13%   | 256K ctx | ~202 tok/s | Runs great  | 95/100 |
| Gemma 4 E2B        | Gemma  | 5d ago | 3.1 GB  | 13%   | 256K ctx | ~202 tok/s | Runs great  | 95/100 |
| Gemma 4 26B-A4B IT | Gemma  | 5d ago | 14.3 GB | 60%   | 256K ctx | ~44 tok/s  | Runs well   | 70/100 |
| Gemma 4 26B-A4B    | Gemma  | 5d ago | 14.3 GB | 60%   | 256K ctx | ~44 tok/s  | Runs well   | 70/100 |
| Gemma 4 31B IT     | Gemma  | 5d ago | 17.4 GB | 73%   | 256K ctx | ~36 tok/s  | Decent      | 61/100 |
| Gemma 4 31B        | Gemma  | 5d ago | 17.4 GB | 73%   | 256K ctx | ~36 tok/s  | Decent      | 61/100 |

Terms:

- E4B - Effective Params - 4 Billions
- A4B - Active Params of a MoE model - 4 Billions
- IT - Industrial Tuned to follow human instructions ()
- non-IT - Base model (just the knowledge, not good for coding)

## Default Model Specs (e4b)

| Spec           | Value                     |
|----------------|---------------------------|
| Parameters     | 4.5B effective            |
| Context window | 128K tokens               |
| Download size  | 9.6GB                     |
| Modality       | Text + Image (multimodal) |
| Vocabulary     | 262K                      |
| Layers         | 60                        |
| Sliding window | 1024 tokens               |

## Usage

```bash
# Start fresh (pulls model automatically)
./stop_clean_start.sh

# Test the model
./test_models.sh

# Remove model weights
./remove_models.sh
```
