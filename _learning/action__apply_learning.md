# Action: Apply Learning

When user says "update learnings" or "let's update our learning", append a dated entry
to `_learning/learnings.md` with insights from the current session.

## What to capture

- **Docker patterns** — image building workflows, volume vs bind mount vs container layer, docker commit gotchas
- **Project conventions** — naming conventions (e.g. mingzilla/ prefix, qwen3pt5 style), port allocation scheme, file structure patterns
- **User preferences** — how the user likes to work (script-driven workflows, draft docs for conversation logging, separation of dev/prod concerns)
- **Ollama/LLM** — model configuration, context window sizing, VRAM considerations, Ollama API compatibility notes

Only capture what's useful for future sessions. Skip anything obvious or already documented
in CLAUDE.md or other project/skill files.

## Entry format

```markdown
### YYYY-MM-DD

- [category] learning text
```

## Rules

- Append to bottom of `_learning/learnings.md`, never delete existing entries
- One entry per session (may contain multiple bullet points)
- Use only what is already in session context — no re-reads to decide what to save
- If nothing worth capturing, say so and skip
