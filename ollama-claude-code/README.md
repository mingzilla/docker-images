# ollama-claude-code

Run Claude Code CLI against a local Ollama server with the qwen3.5 model.

## How it works

Your local `claude` CLI connects to an Ollama Docker container via environment variables:

```bash
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_BASE_URL=http://localhost:40221
ANTHROPIC_API_KEY=""
claude -p "your prompt" --model qwen3.5
```

## Building the image

The goal is to bake the model into a Docker image so it can run without downloading anything.

### Why `docker cp` is needed

`docker commit` only captures a container's **writable layer** — the container's own filesystem. Anything mounted via a **bind mount** or **named volume** is excluded from the commit.

This means:

1. Start a container **with no volume**
2. `docker cp` the model files from `./docker-volumes/models/` into the container's filesystem
3. `docker commit` the container into an image

The local `./docker-volumes/models/` directory acts as a cache. Without it, you'd have to `ollama pull` the model every time you rebuild (~30 min download).

### Workflow

**Step 1: Dev and test** — use `docker-compose.dev.yml`

```bash
docker compose -f docker-compose.dev.yml up -d
# Pull the model (first time only — stored in ./docker-volumes/models/)
docker exec ollama-claude-code-dev ollama pull qwen3.5
# Test
./docker-test.sh
```

This runs base Ollama with a bind mount to `./docker-volumes/models/`. The model is cached locally so you never re-download.

**Step 2: Build the image** — use `docker-build.sh`

```bash
docker compose -f docker-compose.dev.yml down
./docker-build.sh
```

When you're happy with the model, build a standalone image. The script reuses the cached models from `./docker-volumes/models/` and commits as `mingzilla/ollama-claude-code-qwen3pt5:1.0.0`.

**Step 3: Verify the image** — use `docker-compose.yml`

```bash
docker compose up -d
./docker-test.sh
docker compose down
```

Start the baked image and verify it works. No volumes needed — the model is inside the image.

**Step 4: Save (optional)** — use `docker-save.sh`

```bash
./docker-save.sh
```

Export the image to a `.tar` file for portability.

### Scripts

| Script | Purpose |
|---|---|
| `docker-build.sh` | Build the image from cached models in `./docker-volumes/models/` |
| `docker-test.sh` | Test the running container with `claude -p "say hello"` |
| `docker-save.sh` | Export the image to a `.tar` file |

## Files

| File | Description |
|---|---|
| `docker-compose.yml` | Runs the baked image (no volumes) |
| `docker-compose.dev.yml` | Dev: runs base Ollama with bind-mounted models from `./docker-volumes/models/` |
| `docker-volumes/models/` | Cached model files (6.2 GB for qwen3.5 9B) |
