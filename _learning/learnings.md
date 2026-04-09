# Learnings — docker-images

Newest entries at bottom. Never delete entries.

## Entries

### 2026-04-09

- [Docker patterns] `docker commit` only captures a container's writable layer. Bind mounts and named volumes are both excluded. To bake volume data into an image: start container without volume, `docker cp` files in, then commit.
- [Docker patterns] `docker cp ./dir CONTAINER:/path/dir` copies the directory INTO the target, creating nested dirs. Use `docker cp ./dir/. CONTAINER:/path/dir` (trailing `/.`) to copy contents instead.
- [Docker patterns] The ollama Docker image does not include `curl`. Healthchecks inside the container must use `bash /dev/tcp` (`echo > /dev/tcp/localhost/11434`) or check from the host side.
- [Project conventions] Image naming: `mingzilla/ollama-claude-code-qwen3pt5:1.0.0` — model name in the image name, context length omitted (runtime config via `OLLAMA_CONTEXT_LENGTH` env var).
- [Project conventions] Port allocation follows a DEV/PROD scheme (30xxx/40xxx). Tracked in `port_allocation.md` at project root.
- [Project conventions] User uses `_docs/v001/v001__init__01__draft.md` files to log the conversation/decision process. Do not edit these — user maintains them. Solution/plan files are separate (`__02__solution.md`, `__02__plan.md`).
- [User preferences] User prefers script-driven workflows (`docker-build.sh`, `docker-test.sh`, `docker-save.sh`, `docker-load.sh`) over manual docker commands. All scripts should include `cd "$(dirname "$0")"` for run-from-anywhere support.
- [User preferences] User prefers local bind mounts (`./docker-volumes/`) over Docker named volumes for model caching — visible on the filesystem, survives `docker compose down`.
- [Ollama/LLM] Ollama version must be >= 0.17.7 for qwen3.5 tool calling support. Pinned to 0.20.3 as of 2026-04-09.
- [Ollama/LLM] qwen3.5 default is 9B q4_K_M (6.6 GB). On 24GB VRAM (RTX 5090), 64K context is safe (~16.6 GB total). 128K is tight (~26.6 GB). Ollama defaults to 32K for 24GB cards — override with `OLLAMA_CONTEXT_LENGTH`.
- [Ollama/LLM] Claude Code connects to Ollama via 3 env vars: `ANTHROPIC_AUTH_TOKEN=ollama`, `ANTHROPIC_API_KEY=""`, `ANTHROPIC_BASE_URL=http://localhost:<port>`. The Ollama container is just a model server — Claude Code CLI runs on the host.
