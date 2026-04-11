# ollama-gemma4

Ollama container running Google's Gemma 4 model on port **40204**.

## Model Variants

| Variant                | Params         | VRAM needed | Context | Download |
|------------------------|----------------|-------------|---------|----------|
| `gemma4:e2b`           | 2.3B           | ~4GB        | 128K    | 7.2GB    |
| `gemma4:e4b` (default) | 4.5B effective | ~6GB        | 128K    | 9.6GB    |
| `gemma4:26b` (MoE)     | 3.8B active    | ~15-18GB    | 256K    | 18GB     |
| `gemma4:31b` (dense)   | 30.7B          | ~24GB       | 256K    | 20GB     |

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
