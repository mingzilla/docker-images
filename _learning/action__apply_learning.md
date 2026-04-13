# Action: Apply Learning

When user says "update learnings" or "let's update our learning":
1. Read `/mnt/e/code/_notes/ai-agents/.claude/skills/system__manage_learnings/rule__self_evolving.md`, then continue
2. Apply the self-evolving step to the "What to capture" section below
3. Apply the saving step to `_learning/learnings.md`

## What to capture

- **Docker patterns** — image building workflows, volume vs bind mount vs container layer, docker commit gotchas
- **Project conventions** — naming conventions (e.g. mingzilla/ prefix, qwen3pt5 style), port allocation scheme, file structure patterns
- **User preferences** — how the user likes to work (script-driven workflows, draft docs for conversation logging, separation of dev/prod concerns)
- **Ollama/LLM** — model configuration, context window sizing, VRAM considerations, Ollama API compatibility notes
- **Skill integration** — how docker-images projects connect to ai-agents skills (models.yaml, verification setup, CLAUDE.md generation)

Only capture what's useful for future sessions. Skip anything obvious or already documented
in CLAUDE.md or other project/skill files.
