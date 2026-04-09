# Action: Web Search

Search the web using DuckDuckGo via `ddgr`.

## Usage

```bash
${CLAUDE_SKILL_DIR}/scripts/web_search.sh "search query"
```

Returns top 5 results with title, URL, and description.

## Options

```bash
# Custom number of results
${CLAUDE_SKILL_DIR}/scripts/web_search.sh "search query" 10
```

## Output format

Plain text, one result per block:

```
Title
URL
Description
```
