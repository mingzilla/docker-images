# Decision Journal — docker-images

Append-only. Never edit existing entries. Newest at bottom.

## What NOT to capture

- Individual model test results (those go in `_verification/`)
- Ollama config specifics (context length, ports) — those are in compose files and `port_allocation.md`
- Anything about ai-agents skill internals (those decisions belong in the ai-agents skill journal)
- Coding preferences (sh/python conventions) — those stay in learnings for now until a better home is found

## Entries

### 2026-04-12 [L:design decision] [M:architecture] Separate project per model [S:project-structure]

- **Q:** Should all ollama models share one docker-compose or have separate project directories?
- **Options:** (a) single compose with all models, (b) separate directory per model
- **Chose:** separate directory per model
- **Why:** (1) independent lifecycle — stable vs experimental models don't risk each other, (2) clean archival — move whole directory to `_archive/` when obsolete, (3) independent volumes — `clean.sh` in one project can't nuke another model's data
- **Cascade:** unification happens at orchestration layer (`models.yaml` in `tool__local_claude_code`), not at infrastructure

### 2026-04-12 [L:design decision] [M:infrastructure] Named volumes, separate start and pull [S:model-persistence]

- **Q:** How do we avoid re-downloading models after container restarts?
- **Options:** (a) `stop_clean_start.sh` that wipes and re-pulls every time, (b) named volumes with separate start/pull scripts
- **Chose:** named volumes + `pull.sh` separate from `start.sh`
- **Why:** pulling a model takes 10-30 minutes. Wiping volumes on every restart is wasteful. Separation means start is instant, pull is first-time-only.
- **Cascade:** `clean.sh` becomes the nuclear option with confirmation prompt. Normal workflow never touches volumes.

### 2026-04-12 [L:design decision] [M:architecture] Multi-service compose for model variants [S:project-structure] [S:port-allocation]

- **Q:** gemma4 has multiple variants (e4b, 26b). One compose with multiple services, or separate projects?
- **Options:** (a) separate project per variant, (b) one compose with multiple services on different ports
- **Chose:** one compose, two services (`ollama-e4b` on 40204, `ollama-26b` on 40205)
- **Why:** variants share the same model family — they belong together. Can start independently with `docker compose up -d ollama-e4b`. Port allocation updated for both.
- **Cascade:** all scripts take `e4b|26b|all` as argument

### 2026-04-12 [L:design decision] [M:skill-integration] Verification templates in skill, results in model project [S:verification]

- **Q:** Where do model verification test definitions and results live?
- **Options:** (a) both in skill, (b) both in model project, (c) templates in skill, results in model project
- **Chose:** templates in `tool__local_claude_code/assets/verification/`, results in `{compose}/_verification/`
- **Why:** templates are reusable across all models. Results are specific to a model's performance on specific hardware. Output path derived from `compose` field in `models.yaml` — no extra config needed.

### 2026-04-12 [L:design decision] [M:skill-integration] models.yaml as orchestration registry [S:model-registry]

- **Q:** How does the local claude code skill know which models are available?
- **Options:** (a) hardcode in action files, (b) pass params explicitly every time, (c) central registry file
- **Chose:** `models.yaml` with name, tier, port, compose path, service, enabled flag
- **Why:** decouples skill from specific models. Tier selection (`--tier light`) lets callers pick by capability. `enabled` flag allows quick swapping without deleting config.
- **Cascade:** `run.sh` auto-starts containers. `setup.sh` pulls all enabled models. Verification derives output paths.

### 2026-04-13 [L:design decision] [M:model-selection] Reject gemma4, keep qwen3.5 9b [S:model-eval]

- **Q:** Can gemma4 replace qwen3.5 for Claude Code usage?
- **Options:** (a) gemma4:e4b (light), (b) gemma4:26b (MoE heavy), (c) keep qwen3.5 9b
- **Chose:** keep qwen3.5 9b as sole approved model
- **Why:** gemma4 e4b is much slower than qwen3.5 and cannot finish agentic workflows. gemma4 26b is very slow on basic tests and won't complete agentic tasks at all. qwen3.5 fires sub-agents proactively, runs fast, completes all tests correctly.
- **Cascade:** gemma4 models moved to `models_archive.yaml` with rejection dates and reasons. `ollama-gemma4/` to be archived.

### 2026-04-13 [L:design decision] [M:conventions] Rejected models go to archive yaml, not disabled in main [S:model-registry]

- **Q:** How do we handle models that fail evaluation?
- **Options:** (a) set `enabled: false` in `models.yaml`, (b) move to separate `models_archive.yaml`
- **Chose:** separate `models_archive.yaml` with `rejected` date and `reason` fields
- **Why:** clear separation of intent. `enabled: false` means temporarily disabled. Archive means tested and rejected. Future sessions immediately know the model was evaluated and failed.

### 2026-04-14 [L:design decision] [M:skill-integration] Symlink central skills into external projects [S:skill-access]

- **Q:** How do non-ai-agents projects access ai-agents skills?
- **Options:** (a) copy skills into each project, (b) symlink, (c) don't — only use skills from ai-agents
- **Chose:** symlink `.claude/skills` → ai-agents skills dir. Gitignored. `system__save_session` guarded in CLAUDE.md.
- **Why:** skills use absolute paths for scripts, so they work from anywhere. Symlink gives read access without duplication. Guard prevents accidentally saving to ai-agents session logs from wrong project.
- **Cascade:** `action__symlink_to_central_skills` created in `system__manage_skill` to standardise setup across projects.
