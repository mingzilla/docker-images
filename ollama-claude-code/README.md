# ollama-claude-code

Configure Claude Code CLI to use a local Ollama model instead of Anthropic's API.

## Prerequisites

- Ollama running with a model (`ollama-qwen3pt8_27b/` or `ollama-qwen3pt5_9b/` in this repo)
- Claude Code CLI installed on host
- Run `sudo ./install-requirements.sh` for web tools (jq, ddgr, duckdb)

## Usage

One wrapper script per backing model — pick the one whose container is running.

| Script                     | Model         | Port  |
|----------------------------|---------------|-------|
| `./claude-qwen3pt8_27b.sh` | `qwen3.8:27b` | 30214 |
| `./claude-qwen3pt5_9b.sh`  | `qwen3.5`     | 40221 |

```bash
# Interactive mode
./claude-qwen3pt8_27b.sh

# Single-shot mode
./claude-qwen3pt8_27b.sh -p "your prompt"
```

Each script sets the env vars that redirect Claude Code to Ollama:

```bash
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_BASE_URL=http://localhost:30214
ANTHROPIC_API_KEY=""
claude --model qwen3.8:27b
```

## Web tools

Built-in WebSearch and WebFetch do not work with Ollama. This project includes a `tool__web` skill (in `.claude/skills/tool__web/`) that provides shell-based alternatives:

- **Web search**: `ddgr` (DuckDuckGo CLI)
- **Web fetch**: `curl` + HTML text cleaner

The `CLAUDE.md` file instructs Claude Code to use these automatically.

## Files

| File                        | Purpose                                                         |
|-----------------------------|-----------------------------------------------------------------|
| `claude-qwen3pt5_9b.sh`     | Wrapper script to run Claude Code against Ollama (port 40221)   |
| `claude-qwen3pt8_27b.sh`    | Wrapper script for qwen3.8:27b (port 30214)                     |
| `CLAUDE.md`                 | Rules for Claude Code (use web skill, avoid built-in web tools) |
| `install-requirements.sh`   | Install jq, ddgr, duckdb                                        |
| `.claude/skills/tool__web/` | Web search and fetch skill                                      |
| `_docs/`                    | Conversation logs and verification results                      |
