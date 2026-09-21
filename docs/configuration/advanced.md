# Advanced Configuration

Configuration strategies for environment isolation, air-gapped deployments, tool retrieval, and execution controls in OpenJarvis CLI.

---

## 1. Multi-Configuration Workflows

You can maintain distinct configurations tailored for specific workloads:

```text
~/.openjarvis/
├── config.yaml       # Default coordinator setup
├── coding.yaml       # Low-temperature, local code models with compiler tools
└── research.yaml     # High-context models with web and literature tools
```

To invoke OpenJarvis with a specific configuration:

```bash
OJ_CONFIG=~/.openjarvis/coding.yaml openjarvis
# Or via CLI option:
openjarvis --config ~/.openjarvis/coding.yaml
```

---

## 2. Project Workspace Configuration

Place `.openjarvis/config.yaml` in the root of any repository. When executed within that directory tree, OpenJarvis discovers the local configuration and merges it on top of global user defaults (`~/.openjarvis/config.yaml`).

```text
my-project/
├── .openjarvis/
│   ├── config.yaml           # Project-specific agents and execution limits
│   └── config/
│       └── permissions.yaml  # Persisted tool permissions for this repository
├── pyproject.toml
└── src/
```

Workspace-specific configurations override:
- `root_agent` and `agents` definitions.
- `tool_permissions` allowlists, blocklists, and pattern rules.
- Execution limits (`max_active_agents`, `max_spawn_depth`, `max_agent_turns`).

---

## 3. Environment & Credential Resolution

API credentials are resolved from shell environment variables specified by `api_key_env` in profile definitions:

```yaml
root_agent:
  api_key_env: "OPENAI_API_KEY"

agents:
  researcher:
    api_key_env: "ANTHROPIC_API_KEY"
  coder:
    api_key_env: "OPENAI_API_KEY"
```

Export required keys in your environment:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

---

## 4. Air-Gapped & Offline Deployment

In restricted or air-gapped networks, configure OpenJarvis to communicate strictly with local inference endpoints:

```yaml
# .openjarvis/config.yaml
root_agent:
  name: "root"
  role: "coordinator"
  system_prompt: |
    You are the Root Coordinator. Spawn local child agents to solve user tasks.
    Call `complete_task` when all child agents have terminated.
  provider: "ollama"
  base_url: "http://localhost:11434/v1"
  model: "llama3.1"
  temperature: 0.1
  tools:
    - "spawn_agent"
    - "connect_agents"
    - "report_findings"
    - "exit_agent"
    - "complete_task"
    - "read_file"

agents:
  coder:
    role: "coder"
    provider: "ollama"
    base_url: "http://localhost:11434/v1"
    model: "qwen2.5-coder:7b"
    temperature: 0.0
    tools:
      - "str_replace_editor"
      - "bash"
      - "run_python"
      - "run_pytest"
      - "lint_python"

  math:
    role: "math"
    provider: "ollama"
    base_url: "http://localhost:11434/v1"
    model: "llama3.1"
    temperature: 0.0
    tools:
      - "evaluate_expression"
      - "solve_equation"
      - "convert_units"
      - "prime_factorize"
```

In offline environments, all deterministic local tools (`read_file`, `write_file`, `str_replace_editor`, `bash`, `run_python`, `run_pytest`, `evaluate_expression`, `parse_json`, etc.) operate without network egress.

---

## 5. Tool Scoping & Two-Phase Retrieval (Tool RAG)

### Scoped Tool Allowlists
You can restrict tool access per agent profile:

```yaml
agents:
  math:
    # Only mathematical calculation tools
    tools:
      - "evaluate_expression"
      - "solve_equation"
      - "convert_units"
      - "prime_factorize"

  writer:
    # Pure reasoning agent: no tools exposed
    tools: []

  operator:
    # Unrestricted access to all registered tools
    tools: null
```

### Two-Phase Tool Retrieval (FastEmbed)
When the tool catalog is extensive, enable semantic tool retrieval:

```yaml
tool_retrieval:
  enabled: true
  top_k: 5
  similarity_threshold: 0.35
  always_on_tools:
    - "read_file"
    - "spawn_agent"
    - "exit_agent"
```

- **Scope-Constrained Indexing**: Retrieval is constrained strictly within the agent's permitted `tools` list. Unpermitted tools are never indexed or exposed.
- **Always-On Pinning**: Specified tools in `always_on_tools` are always bound to the model schema regardless of query relevance.
- **Execution Guard**: If an unpermitted tool name is generated, the invocation is intercepted and denied before execution.

---

## 6. Execution Limits & Concurrency Caps

Control resource consumption across concurrent actor nodes:

```yaml
limits:
  max_active_agents: 8          # Maximum concurrent active agent nodes in the MAS graph
  max_spawn_depth: 3            # Maximum parent-to-child spawning depth
  max_agent_turns: 15           # Maximum turns per agent before termination
  turn_timeout_seconds: 300.0   # Per-turn wall-clock timeout
```

---

## See Also

- [Configuration Overview](overview.md)
- [Agents & Profiles](agents.md)
- [Providers Guide](providers.md)
- [Security & Permissions](../security.md)
