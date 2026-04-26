# Rule: docker-images

> Goal: <to fill — one-line statement of what this rule is trying to achieve>
> Capture Statement: Before adding content, run the Capture gate; if Unsure, ask the user and write the discriminator back into the relevant slot; then append.
>
> Inherits machinery (General Rule Schema, Default invariants, Update classifier cascade pattern, locked base node, Y/n/unsure primitive) from `evolution__general_rule.md`.

## Self Evolving

### General Rule Content (filling the 5 locked General slots)

- **Trigger condition:** <to fill — when this rule runs, wording per `principles__use_llm.md` §7>
- **Capture gate:** Clear yes / Clear no / Unsure applied to: Only capture what's useful for future sessions. Skip anything obvious or already documented in CLAUDE.md or other project/skill files.
- **Duplication check:** <to fill — how to compare before appending>
- **Size management:** <to fill — threshold and response>
- **Supersession:** <to fill — how current vs historical is marked>

<!-- Default invariants (Self-sharpening, Session-context-only, Append-only, Skip-if-empty) are inherited from evolution__general_rule.md — do not restate here. -->

### Specific Rule Schema + Content

| Format       | Name                  | Purpose                                                                                                                              | Emit when |
|--------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------|-----------|
| bullet point | Docker patterns       | image building workflows, volume vs bind mount vs container layer, docker commit gotchas                                              | always    |
| bullet point | Project conventions   | naming conventions (e.g. mingzilla/ prefix, qwen3pt5 style), port allocation scheme, file structure patterns                          | always    |
| bullet point | User preferences      | how the user likes to work (script-driven workflows, draft docs for conversation logging, separation of dev/prod concerns)            | always    |
| bullet point | Ollama/LLM            | model configuration, context window sizing, VRAM considerations, Ollama API compatibility notes                                       | always    |
| bullet point | Skill integration     | how docker-images projects connect to ai-agents skills (models.yaml, verification setup, CLAUDE.md generation)                        | always    |

- **Docker patterns:** <to fill>
- **Project conventions:** <to fill>
- **User preferences:** <to fill>
- **Ollama/LLM:** <to fill>
- **Skill integration:** <to fill>

### Update classifier

The locked base node fires first (see `evolution__general_rule.md` § Locked base node). Then project-specific nodes:

1. **<to fill — first project-specific signal as a question>?**
    - Yes → <leaf action>.
    - No → continue.
    - Unsure → ask user.

… (additional project-specific nodes as needed) …

## Content Schema

| Format | Name | Purpose | Emit when |
|--------|------|---------|-----------|

<to fill — entry template for `learnings.md`>

## Content

<see _meta/_learning/learnings.md>
