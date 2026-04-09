# ollama-claude-code

Configure Claude Code CLI to use a local Ollama model instead of Anthropic's API.

## Prerequisites

- Ollama running with a model (e.g. `ollama-qwen3pt5_9b/` in this repo)
- Claude Code CLI installed on host
- Run `sudo ./install-requirements.sh` for web tools (jq, ddgr, duckdb)

## Usage

```bash
# Interactive mode
./claude-qwen.sh

# Single-shot mode
./claude-qwen.sh -p "your prompt"
```

This sets the env vars that redirect Claude Code to Ollama:

```bash
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_BASE_URL=http://localhost:40221
ANTHROPIC_API_KEY=""
claude --model qwen3.5
```

## Web tools

Built-in WebSearch and WebFetch do not work with Ollama. This project includes a `tool__web` skill (in `.claude/skills/tool__web/`) that provides shell-based alternatives:

- **Web search**: `ddgr` (DuckDuckGo CLI)
- **Web fetch**: `curl` + HTML text cleaner

The `CLAUDE.md` file instructs Claude Code to use these automatically.

## Files

| File                        | Purpose                                                         |
|-----------------------------|-----------------------------------------------------------------|
| `claude-qwen3pt5_9b.sh`     | Wrapper script to run Claude Code against Ollama                |
| `CLAUDE.md`                 | Rules for Claude Code (use web skill, avoid built-in web tools) |
| `install-requirements.sh`   | Install jq, ddgr, duckdb                                        |
| `.claude/skills/tool__web/` | Web search and fetch skill                                      |
| `_docs/`                    | Conversation logs and verification results                      |
