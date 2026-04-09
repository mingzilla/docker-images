---
name: tool__web
description: Web search and fetch for environments without built-in web tools. TRIGGER when: web search or web fetch fails, or when using Ollama/local model backend.
user-invocable: true
allowed-tools: Read Bash
---

Shell-based web search and fetch. Use when built-in web tools are unavailable (e.g. Ollama-backed Claude Code).

## When to use

- **search** — need to find URLs or information about a topic
- **fetch** — have a URL, need its content as clean text

## Available actions

- `action__search` — search the web using ddgr (DuckDuckGo)
- `action__fetch` — fetch a URL and extract clean text

## Requirements

- `ddgr` — DuckDuckGo CLI (for search)
- `curl` — HTTP client (for fetch)
- `python3` — required by text cleaner (for fetch)
