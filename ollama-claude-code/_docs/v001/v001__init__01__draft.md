could you set up ollama claude code for me following:
https://docs.ollama.com/integrations/claude-code

just use qwen3.5 model

read ollama-claude-code/docker-compose.yml first, it has the initial structure with port

---

● Here are my thoughts on the draft:

  What it's asking for: Set up Ollama as a Claude Code backend using the qwen3.5 model, containerized via Docker.

  The docker-compose.yml is a solid start, but has gaps:

  1. No volume for model persistence. If the container restarts, all pulled models (qwen3.5 etc.) are lost. Following the project convention, it should have something like:
  volumes:
    - ollama-claude-code__models:/root/.ollama
  2. No model auto-pull. After the container starts, qwen3.5 still needs to be pulled manually (ollama pull qwen3.5). Could be handled by an init script or a post-start command.
  3. Image version is TBD. The comment # find specific version to put here — worth pinning to a specific tag for reproducibility.

  On the Claude Code integration side, the draft doesn't cover:

  4. Client-side configuration. Claude Code needs three env vars to talk to Ollama:
    - ANTHROPIC_AUTH_TOKEN=ollama
    - ANTHROPIC_API_KEY=""
    - ANTHROPIC_BASE_URL=http://localhost:40203 (the exposed port)

  This is the key piece — how/where these get set (shell profile, a wrapper script, Claude Code settings) should be documented.
  5. Context window consideration. Ollama docs recommend 64k+ tokens minimum. The default qwen3.5 context may be smaller — might need num_ctx configured in a Modelfile or at
  request time.
  6. No mention of whether this is for local dev use or shared. Affects whether the port binding should be 127.0.0.1:40203:11434 (local only) vs 0.0.0.0.

  Overall: The draft is a reasonable starting point as a task description. The docker-compose is 80% there — mainly needs a volume and the client-side setup instructions. Want me
  to implement it?
  
---

❯ 1
  ok, i do not want to volume out the model, i would like the model to be kept in the docker container, then i rebuild the container as a image
  i typically just save the model as a local file, it does not have to be published to docker hub
  i have just made a docker-compose.dev.yml file, which is to be used for creating this local jar file image
  docker-compose.yml will just run with this jar file

  2
  part of docker-compose.dev.yml

  3
  that's a comment i specific write there, asking you to find out what version of ollama to use. we can just download the latest version, then lock to that version afterwards
  i had experience using later ollama versions and it no longer work with certain models any more

  5
  my machine is a RTX5090 24gb vram laptop, i want to use 128k tokens context window because that's what this model supports. unless my machine is not capable of handling this

  6
  0.0.0.0 please

---

## Research Findings

### Ollama Version
- Latest stable: **0.20.3** (published 2026-04-07)
- Minimum for Claude Code (Anthropic Messages API): **v0.14.0**
- Minimum for qwen3.5 tool calling fix: **v0.17.7** (earlier versions used wrong tool-call parser)
- **Pin to: `ollama/ollama:0.20.3`**

### Model: qwen3.5
- Default `ollama pull qwen3.5` → **9B q4_K_M** (6.6 GB)
- All variants support up to **256K context** natively
- Available sizes for 24GB VRAM (RTX 5090):

| Variant | Size | VRAM | Notes |
|---------|------|------|-------|
| `qwen3.5` (9b default) | 6.6 GB | Plenty of headroom | Good for 128K context |
| `qwen3.5:27b` | 17 GB | Tight with 128K ctx | Dense, all 27B params active |
| `qwen3.5:35b` (35B-A3B MoE) | 24 GB | Very tight | Only 3B active per token, fast |
| `qwen3.5:35b-a3b-int4` | 20 GB | Better headroom | MoE + int4 quant |
| `qwen3.5:35b-a3b-nvfp4` | 22 GB | Moderate headroom | MoE + nvfp4 quant |
| `qwen3.5:27b-coding-nvfp4` | 20 GB | Better headroom | Coding-specific variant |

- **128K context KV cache consideration**: An 8B model goes from ~0.3 GB (2K ctx) to ~20 GB (128K ctx) of KV cache. For the 9B default at 128K, total VRAM ≈ 6.6 GB weights + ~20 GB KV cache ≈ 26.6 GB — tight on 24 GB. May need to use a smaller context or smaller quantization.
- For **safe 128K on 24GB**: `qwen3.5` (9b) should work but will be near the limit. If OOM issues occur, reduce to 64K or use `qwen3.5:4b`.

### Context Window Configuration
- Ollama auto-detection for 24GB VRAM defaults to **32K** context
- To set 128K: add env var `OLLAMA_CONTEXT_LENGTH=131072` in docker-compose
- Alternative: bake it into a Modelfile with `PARAMETER num_ctx 131072`

### Claude Code Client Configuration
Three env vars needed to connect Claude Code to Ollama:
```bash
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_API_KEY=""
ANTHROPIC_BASE_URL=http://localhost:40203
```

Run with:
```bash
ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40203 ANTHROPIC_API_KEY="" claude --model qwen3.5
```

### Port Allocation Conflict
⚠️ Port 40203 (dev: 30203) is currently assigned to **both** `google/gemma-2-2b-it` and `ollama claude code` in `port_allocation.md`. Need to resolve — either retire the gemma entry or assign a new port.

---

## Implementation Plan

### Workflow: Bake Model into Docker Image

1. **Dev phase** (`docker-compose.dev.yml`):
   - Start ollama container from `ollama/ollama:0.20.3`
   - Pull qwen3.5 model inside the container
   - Commit the container as a local image (e.g., `ollama-claude-code:1.0.0`)

2. **Prod phase** (`docker-compose.yml`):
   - Run from the committed local image `ollama-claude-code:1.0.0`
   - Model is already baked in, no pull needed

### Files to Create/Modify

1. **`docker-compose.dev.yml`** — for building the image:
   - Pin `ollama/ollama:0.20.3`
   - Add `OLLAMA_CONTEXT_LENGTH=131072`
   - Container name: `ollama-claude-code-dev`

2. **`docker-compose.yml`** — for running the baked image:
   - Use local image `ollama-claude-code:1.0.0`
   - Add `OLLAMA_CONTEXT_LENGTH=131072`
   - Container name: `ollama-claude-code`

3. **`build.sh`** — script to automate the build workflow:
   - Start dev container
   - Wait for health check
   - Pull model inside container
   - Stop container
   - Commit container to local image
   - Clean up dev container

4. **`port_allocation.md`** — fix the port conflict

---

## Decision Points (for user)

1. **Model size**: Default `qwen3.5` (9b, 6.6 GB) — or a larger variant? The 9b with 128K context will use ~26 GB total which is near/over 24 GB VRAM limit. Options:
   - Use 9b with 128K and see if it fits (VRAM may be managed with flash attention)
   - Use 9b with 64K context (safer)
   - Use `qwen3.5:4b` with 128K context (definitely fits)
   - Use `qwen3.5:35b-a3b-int4` (20 GB weights, but MoE uses less KV cache per active param)

2. **Port conflict**: Keep 40203 for ollama-claude-code and retire/reassign gemma-2-2b-it?

3. **Image naming convention**: `ollama-claude-code:1.0.0` — or follow existing naming like `mingzilla/ollama-claude-code:1.0.0`?

---

❯ 1
  Use 9b with 64K context. Primary use case is `claude -p <prompt>` (non-interactive single-shot).
  With `-p` mode, each invocation is independent — no conversation history reprocessing.
  64K is generous for single-shot prompts. VRAM: 6.6 GB weights + ~10 GB KV cache ≈ 16.6 GB, plenty of headroom.

  2
  Port: 40221 (dev: 30221)

  3
  Image: mingzilla/ollama-claude-code:1.0.0

---

### `claude -p` with Ollama — confirmed working

`claude -p` is non-interactive mode — sends a single request to whatever backend is configured. Works with Ollama:

```bash
ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" claude -p "your prompt" --model qwen3.5
```

Context efficiency note: In interactive mode, every follow-up reprocesses full conversation history. With `-p`, each call is fresh — no accumulated history waste. 64K is a good fit.

Suggested convenience alias:
```bash
alias claude-local='ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=http://localhost:40221 ANTHROPIC_API_KEY="" claude --model qwen3.5'
# Usage: claude-local -p "your prompt"
```

### Remaining question

`build.sh` will do: start container → pull model → stop → `docker commit`. Should it also `docker save` the image to a `.tar` file for portability, or is just having it in the local Docker image store sufficient?

---

  we will have a docker-build.sh file to build, and docker-save.sh to save.
  we should be able to test the docker container before we save the tar file to be used by docker-compose.yml, right?

● Yes, exactly. The workflow would be:

  1. docker-build.sh — start dev container, pull model, commit as mingzilla/ollama-claude-code:1.0.0
  2. Test — run the image directly (docker run or a quick docker-compose.dev.yml variation) and verify claude -p works against it
  3. docker-save.sh — once satisfied, export to .tar
  4. docker-compose.yml — runs from the saved image

  The committed image lives in your local Docker store after step 1, so you can test it immediately without saving to .tar first. The .tar is just for archiving/portability.

  Ready to write the plan to ollama-claude-code/_docs/v001/v001__init__02__plan.md whenever you give the go-ahead.