# Configuration Overview

OpenJarvis uses a unified YAML configuration file (`config.yaml`) to define the Multi-Agent System: the primary user-facing Root Agent, reusable agent profiles, domain specialists, and runtime guardrails.

---

## Configuration Discovery Order

When you launch `openjarvis` or `oj`, the CLI automatically locates your configuration using this search order:

1. **`OJ_CONFIG` environment variable** (highest priority):
   ```bash
   export OJ_CONFIG=/path/to/custom-config.yaml
   openjarvis
   ```
2. **Local project workspace**:
   - `./.openjarvis/config.yaml`
   - `./.openjarvis/config/config.yaml`
3. **Global user configuration**:
   - `~/.openjarvis/config.yaml`
   - `~/.openjarvis/config/config.yaml`
4. **System-wide configuration**: `/etc/openjarvis/config.yaml` (Linux / macOS only)

When both global and local configurations exist, OpenJarvis automatically merges them: local workspace settings override global user defaults.

If no configuration file is detected in any location, OpenJarvis automatically launches the **interactive setup wizard** to configure your provider and write your initial `config.yaml`.

---

## Canonical Configuration Structure

A complete configuration defines the Root Agent, agent profiles, domain specialists, and multi-agent limits:

```yaml
# ----------------------------------------------------------------------
# Root Coordinator (Direct User Communication & Primary Orchestrator)
# ----------------------------------------------------------------------
root_agent:
  name: "root"
  role: "coordinator"
  description: "Primary user-facing coordinator managing multi-agent tasks."
  system_prompt: |
    You are the Root Agent of OpenJarvis, directly responsible for user communication
    and multi-agent orchestration. Spawn specialized child agents with `spawn_agent`
    when needed, connect agents with `connect_agents`, monitor their findings, and call `complete_task`
    when all children have exited and their work is synthesized.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.1
  max_hops: 15

# ----------------------------------------------------------------------
# Pre-Configured Agent Profiles (Spawnable by Root or Child Agents)
# ----------------------------------------------------------------------
agents:
  researcher:
    name: "researcher"
    role: "researcher"
    description: "Deep factual research, web queries, and documentation lookup."
    system_prompt: |
      You are the RESEARCHER agent in OpenJarvis. Gather facts, search documentation,
      report findings with `report_findings`, and exit with `exit_agent`.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    temperature: 0.2
    tools:
      - "fetch_webpage"
      - "search_web"
      - "query_wikipedia"

  coder:
    name: "coder"
    role: "coder"
    description: "Software engineering, file editing, debugging, and code execution."
    system_prompt: |
      You are the CODER agent in OpenJarvis. Write, debug, refactor, and test code.
      Report findings with `report_findings`, and exit with `exit_agent`.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    temperature: 0.0
    tools:
      - "str_replace_editor"
      - "bash"
      - "execute_python"
      - "lint_python_code"
      - "git_status"
      - "git_diff"

# ----------------------------------------------------------------------
# Inner Domain Specialists (For Internal Conductor Delegation)
# ----------------------------------------------------------------------
specialists:
  math:
    name: "math"
    description: "Calculations, equations, statistics."
    system_prompt: "You are the MATH specialist. Solve quantitative problems with rigor."
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    delegates_to: ["code"]
    tools:
      - "calculator"
      - "evaluate_expression"

# ----------------------------------------------------------------------
# Multi-Agent Resource & Safety Limits
# ----------------------------------------------------------------------
limits:
  max_active_agents: 8          # Maximum concurrent active agent nodes
  max_spawn_depth: 3            # Maximum nesting depth from Root Agent
  max_agent_turns: 15           # Maximum message exchanges per agent before forced exit
  turn_timeout_seconds: 300.0   # Wall-clock timeout per agent step
```
