# Configuration Overview

OpenJarvis CLI uses a YAML configuration file (`config.yaml`) to specify the Multi-Agent System: the root coordinator, agent profiles, tool permissions, retrieval parameters, and execution limits.

---

## Configuration Discovery Order

When launched via `openjarvis` or `oj`, the configuration file is resolved in the following priority:

1. **`OJ_CONFIG` environment variable**:
   ```bash
   export OJ_CONFIG=/path/to/custom-config.yaml
   openjarvis
   ```
2. **Explicit CLI flag**:
   ```bash
   openjarvis --config /path/to/custom-config.yaml
   ```
3. **Workspace-local configuration**:
   - `./.openjarvis/config.yaml`
   - `./.openjarvis/config/config.yaml`
4. **Global user configuration**:
   - `~/.openjarvis/config.yaml`
   - `~/.openjarvis/config/config.yaml`
5. **System-wide configuration**: `/etc/openjarvis/config.yaml` (Linux / macOS)

When both global and workspace configurations exist, OpenJarvis merges them: workspace settings override global defaults. If no configuration exists, the interactive setup wizard is launched.

---

## Canonical Configuration Schema

```yaml
# .openjarvis/config.yaml

# ----------------------------------------------------------------------
# Root Agent (Top-Level Coordinator)
# ----------------------------------------------------------------------
root_agent:
  name: "root"
  role: "coordinator"
  description: "Primary orchestrator for multi-agent execution."
  system_prompt: |
    You are the Root Coordinator of OpenJarvis. Coordinate execution across
    specialized child agents via `spawn_agent`, link communication channels
    via `connect_agents`, aggregate findings, and call `complete_task` when
    all objectives are met.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.1
  timeout: 60.0
  max_hops: 15
  tools:
    - "spawn_agent"
    - "connect_agents"
    - "report_findings"
    - "exit_agent"
    - "complete_task"
    - "read_file"
    - "search_dir"

# ----------------------------------------------------------------------
# Agent Profiles (Spawnable Worker Agents)
# ----------------------------------------------------------------------
agents:
  researcher:
    name: "researcher"
    role: "researcher"
    description: "Factual research, web queries, and documentation retrieval."
    system_prompt: |
      You are the RESEARCHER agent in OpenJarvis. Investigate questions,
      gather sources, report findings with `report_findings`, and terminate with `exit_agent`.
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.2
    tools:
      - "search_web"
      - "fetch_url"
      - "fetch_wikipedia"
      - "read_file"

  coder:
    name: "coder"
    role: "coder"
    description: "Software engineering, file editing, and testing."
    system_prompt: |
      You are the CODER agent in OpenJarvis. Write, edit, and test source code.
      Report results with `report_findings`, and terminate with `exit_agent`.
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.1
    tools:
      - "str_replace_editor"
      - "bash"
      - "run_python"
      - "run_pytest"
      - "lint_python"
      - "git_status"
      - "git_diff"

  math:
    name: "math"
    role: "math"
    description: "Symbolic mathematics, arithmetic, and unit conversion."
    system_prompt: |
      You are the MATH agent in OpenJarvis. Solve mathematical and numerical tasks.
      Report findings with `report_findings`, and terminate with `exit_agent`.
    provider: "openai"
    model: "gpt-4o"
    temperature: 0.0
    tools:
      - "evaluate_expression"
      - "solve_equation"
      - "convert_units"
      - "prime_factorize"

# ----------------------------------------------------------------------
# Tool Permissions & Security Policy
# ----------------------------------------------------------------------
tool_permissions:
  mode: "interactive"  # "interactive" | "autonomous" | "allowlist"
  allowed_tools:
    - "read_file"
    - "search_dir"
    - "search_in_files"
    - "git_status"
    - "git_diff"
  blocked_tools:
    - "delete_file"
  rules:
    bash:
      argument_patterns:
        - match:
            command: "git status*"
          action: "allow"
        - match:
            command: "pytest*"
          action: "allow"
        - match:
            command: "rm -rf*"
          action: "deny"
      default_action: "confirm"

# ----------------------------------------------------------------------
# Multi-Agent Execution Limits
# ----------------------------------------------------------------------
limits:
  max_active_agents: 8          # Maximum concurrent active actor nodes
  max_spawn_depth: 3            # Maximum nesting depth from root agent
  max_agent_turns: 15           # Maximum turn iterations per agent
  turn_timeout_seconds: 300.0   # Timeout per agent step in seconds
```

---

## Configuration Fields

### Root Agent & Agent Profiles (`AgentProfileConfig`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | required | Unique identifier for the agent profile. |
| `role` | string | `"generalist"` | Functional role (e.g. `coordinator`, `coder`, `researcher`). |
| `description` | string | `null` | Summary of profile responsibilities. |
| `system_prompt` | string | required | Instructions defining persona and response constraints. |
| `provider` | string | `"openai"` | LLM provider backend (`openai`, `anthropic`, `gemini`, `ollama`). |
| `base_url` | string | `"http://localhost:11434/v1"` | API base URL. |
| `model` | string | `"llama3"` | Model identifier. |
| `api_key_env` | string | `null` | Name of environment variable containing API key. |
| `temperature` | float | `0.7` | Sampling temperature ($0.0$ to $2.0$). |
| `max_tokens` | integer | `null` | Maximum tokens per response. |
| `timeout` | float | `60.0` | HTTP request timeout in seconds. |
| `tools` | list[string] | `null` | Allowed tool subset. If `null`, all registered tools are permitted. |
| `max_hops` | integer | `10` | Maximum internal hops per turn for this conductor. |

### Execution Limits (`MultiAgentLimitsConfig`)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `max_active_agents` | integer | `8` | Maximum concurrent active agent nodes in the MAS graph. |
| `max_spawn_depth` | integer | `3` | Maximum nesting depth allowed when spawning sub-agents. |
| `max_agent_turns` | integer | `15` | Maximum iterations an agent can run before forced termination. |
| `turn_timeout_seconds` | float | `300.0` | Maximum wall-clock time allocated to an agent turn. |

---

## Next Steps

- **[Agents & Profiles →](agents.md)**: Role scoping, inheritance, and parameter customization.
- **[Providers & Endpoints →](providers.md)**: Setup guides for OpenAI, Anthropic, Gemini, and Ollama.
- **[Advanced Configuration →](advanced.md)**: Tool RAG, limits, and blackboard storage configuration.
- **[Security & Permissions →](../security.md)**: Deep dive into permission rules and operating modes.
