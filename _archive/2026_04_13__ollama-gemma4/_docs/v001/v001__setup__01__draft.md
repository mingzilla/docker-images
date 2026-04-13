this is created to mirror ollama-qwen3pt5_9b, which is fantastic
now what's missing is, 
- this project needs to support 2 models: gemma4:e4b, gemma4:26b, see ollama-gemma4/readme.md
- i don't want to use ollama-gemma4/stop_clean_start.sh to wipe things out all the time
- if a model is downloaded to my machine, i don't want to waste half an hour to download it again
- but then at the same time i don't want a system to always download 2 models if only 1 is used
- i don't mind the 2 models running on different ports, that gives me the flexibility of running them at the same time or just run one
- this would be good because i want to potentially use claude code to launch sub-agents using a small model for small tasks
- potentially in the future if this works, i don't see why i can't launch ollama-qwen3pt5_9b on demand to do work
- ports: port_allocation.md
- there is actually a skill available: ai-agents/.claude/skills/tool__local_claude_code
- if needed, docker-images/.claude/ can symlink skills to the ai-agents/.claude/skills/ folder to get all the skills (if we do that we make a script, because the symlink needs to be gitignored to avoid git issues)

thoughts please

❯ 1
  we want 2 ports, we just update the port md file to have 2

  2
  correct non wsl path E:\code\_notes\ai-agents\.claude\skills

  thoughts please

  Read 4 files, listed 3 directories (ctrl+o to expand)

● Now I have the full picture. Here are my thoughts:

  1. Two ports — straightforward

  Update port_allocation.md to split gemma4 into two rows:

  | Completions | google/gemma4:e4b | 30204 | 40204 |
  | Completions | google/gemma4:26b | 30205 | 40205 |

  Two services in one docker-compose, each with its own named volume. Scripts accept e4b or 26b as argument.

  2. The tool__local_claude_code skill already does what you need

  It's model and port agnostic — run.sh <port> <model> "<prompt>". So it already works with gemma4:

  run.sh 40204 gemma4:e4b "lightweight task"
  run.sh 40205 gemma4:26b "heavier task"
  run.sh 40221 qwen3.5 "qwen task"

  No changes needed to the skill itself. The question is just making it available from docker-images/.

  3. Symlinking skills — I'd hold off for now

  Reason: docker-images/ is infrastructure (containers, ports, scripts). The skill lives in ai-agents/ which is the agent orchestration layer. The skill
  already works cross-project because run.sh uses absolute paths and claude -p. Symlinking couples the two repos and adds gitignore ceremony for no
  immediate gain.

  If you do want it later, a simple setup-skills.sh that does ln -sf /mnt/e/code/_notes/ai-agents/.claude/skills/tool__local_claude_code .claude/skills/ +
  adds the symlink to .gitignore would work. But I'd only do it when there's a concrete use case that requires it.

  Want me to proceed with building the two-service setup for ollama-gemma4?

❯ good thinking

  ok, so docker-images/ has the qwen and gemma docker setup
  how do we seamlessly use the local claude code skill to launch a container (we provide some hard coded options somewhere so that the skill can pick one
  to use adaptively) and run e.g. sub-agents?

● Good question. Let me think through this end-to-end.

  The gap today: run.sh requires the caller to know the port, model name, and assumes the container is already running. For seamless sub-agent usage, Claude
   Code (the orchestrating session) shouldn't need to think about any of that.

  Proposed design:

  A registry file — lives alongside the skill, declares what's available:

  # tool__local_claude_code/models.yaml
  models:
    - name: qwen3.5
      tier: light
      port: 40221
      compose: /mnt/e/code/docker-images/ollama-qwen3pt5_9b

    - name: gemma4:e4b
      tier: light
      port: 40204
      compose: /mnt/e/code/docker-images/ollama-gemma4
      service: ollama-e4b

    - name: gemma4:26b
      tier: heavy
      port: 40205
      compose: /mnt/e/code/docker-images/ollama-gemma4
      service: ollama-26b

  An enhanced run.sh — three usage modes:

  # Explicit: caller picks the model
  run.sh --model gemma4:e4b "summarise this"

  # By tier: skill picks the best available in that tier
  run.sh --tier light "summarise this"

  # Auto: skill picks based on prompt length / complexity heuristic
  run.sh "summarise this"

  The script would:
  1. Read models.yaml to resolve port + model
  2. Health-check the port
  3. If not running → docker compose -f ... up -d <service> + wait for healthy + ollama pull if needed
  4. Run claude -p

  The "tier" concept is the key bit. It means the orchestrating Claude session just says "run this on a light model" without caring whether that's qwen,
  gemma4:e4b, or something you add later. You swap models in the registry, callers don't change.

  On auto-start: the pull step is the slow part (first time only). After that, start is seconds. So the flow is:
  - First use ever: ~minutes (pull)
  - Container stopped: ~5s (start + health check)
  - Container running: instant

  Where things live:

  ┌────────────────────────┬───────────────────────────────────────────────────────────┬──────────────────────────────────────┐
  │          What          │                           Where                           │                 Why                  │
  ├────────────────────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ Registry (models.yaml) │ ai-agents/.claude/skills/tool__local_claude_code/         │ It's orchestration config, not infra │
  ├────────────────────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ Docker compose files   │ docker-images/ollama-*/                                   │ Infrastructure stays here            │
  ├────────────────────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────┤
  │ Enhanced run.sh        │ ai-agents/.claude/skills/tool__local_claude_code/scripts/ │ Skill owns its scripts               │
  └────────────────────────┴───────────────────────────────────────────────────────────┴──────────────────────────────────────┘

  The skill stays self-contained in ai-agents/ — it just knows the absolute paths to docker-compose files in docker-images/. No symlinking needed.

  Thoughts? Want me to build this, or should we get the two-service docker-compose working first and layer this on after?

❯ this makes me feel like we may want to keep the 2 projects quite close to each other. (just thoughts)

  on the models.yaml file, i would add `enabled: true/false` for each option, just so that i don't need to delete a setup if i want to swap to something
  else to do a quick test

  it's probably better to suggest model downloading upfront if possible. (for the enabled ones). if not it's fine, no need to overcomplicate a solution if
  that is not very straightforward

  thoughts please

● On keeping projects close:

  They already are — both sit under /mnt/e/code/. The registry just uses absolute paths. No need to merge or restructure. If you ever move things, you
  update models.yaml — one file, one place.

  On enabled: true/false:

  Good call. Clean way to keep configs around without them being active:

  models:
    - name: qwen3.5
      tier: light
      port: 40221
      compose: /mnt/e/code/docker-images/ollama-qwen3pt5_9b
      enabled: true

    - name: gemma4:e4b
      tier: light
      port: 40204
      compose: /mnt/e/code/docker-images/ollama-gemma4
      service: ollama-e4b
      enabled: true

    - name: gemma4:26b
      tier: heavy
      port: 40205
      compose: /mnt/e/code/docker-images/ollama-gemma4
      service: ollama-26b
      enabled: false

  Tier selection only considers enabled: true entries. Simple.

  On upfront model downloading:

  Straightforward actually. A setup.sh script that:

  1. Reads models.yaml
  2. For each enabled: true entry — starts the container, pulls the model, stops the container
  3. Reports what's ready

  # One-time setup
  bash tool__local_claude_code/scripts/setup.sh

  # Output:
  # qwen3.5 on 40221 — already pulled ✓
  # gemma4:e4b on 40204 — pulling... done ✓
  # gemma4:26b on 40205 — skipped (disabled)

  You run this once when you add a new model. After that, run.sh never hits the slow pull path. Keeps run.sh simple — it just starts and runs, no pull logic
   needed.

  So the build order would be:

  1. Two-service docker-compose in ollama-gemma4/ (infra)
  2. Update port_allocation.md
  3. Enhanced skill in ai-agents/: models.yaml + updated run.sh + setup.sh

  Want me to start with step 1?