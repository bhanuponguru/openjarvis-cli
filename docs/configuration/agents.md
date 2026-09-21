# Agents & Profiles Configuration

OpenJarvis models execution nodes in the Multi-Agent System (MAS) as autonomous **Conductor** instances. Profiles are declared under `agents:` and `root_agent:` in the configuration file.

---

## Agent Configuration Schema

Each profile under `agents:` configures persona, model hyperparameters, execution boundaries, and permitted tools:

```yaml
agents:
  <agent_name>:
    name: "<agent_name>"            # Profile identifier
    role: "<role>"                  # Functional role label (e.g. researcher, coder, math)
    description: "..."              # Summary of role capabilities
    system_prompt: |                # System prompt instructions defining role boundaries
      You are the ...
    provider: "openai"              # Provider type (openai, anthropic, gemini, ollama)
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    api_key_env: "OPENAI_API_KEY"   # Environment variable holding API key
    temperature: 0.1                # Sampling temperature
    max_tokens: 4096                # Maximum generation tokens
    timeout: 60.0                   # Per-request HTTP timeout in seconds
    max_hops: 10                    # Hop limit for this agent's internal conductor turn
    tools:                          # Permitted tool list (null permits all tools)
      - "str_replace_editor"
      - "bash"
      - "run_python"
      - "run_pytest"
```

---

## Canonical Agent Profiles

### 1. Researcher (`researcher`)
- **Role**: Factual verification, web searches, and documentation lookup.
- **Default Tools**: `search_web`, `fetch_url`, `fetch_wikipedia`, `read_file`.
- **Function**: Ingests external web data, summarizes findings, and passes structured summaries to neighbor agents via `report_findings`.

### 2. Coder (`coder`)
- **Role**: Software engineering, file editing, syntax verification, and test execution.
- **Default Tools**: `str_replace_editor`, `bash`, `run_python`, `run_pytest`, `lint_python`, `git_status`, `git_diff`, `apply_patch`.
- **Function**: Inspects, edits, and verifies source code. Generates code deliverables and test outputs.

### 3. Math Specialist (`math`)
- **Role**: Quantitative reasoning, arithmetic, symbolic algebra, and unit conversion.
- **Default Tools**: `evaluate_expression`, `solve_equation`, `convert_units`, `prime_factorize`.
- **Function**: Solves numeric expressions and equation systems with symbolic precision.

### 4. Planner (`planner`)
- **Role**: Task decomposition, timeline analysis, and schedule tracking.
- **Default Tools**: `get_current_datetime`, `date_arithmetic`, `days_between`, `format_datetime`.
- **Function**: Evaluates milestone dependencies and decomposes user goals into structured sub-tasks.

---

## Dynamic Runtime Instantiation

Agents can dynamically spawn subordinate agents using the `spawn_agent` meta-tool:

```json
{
  "role": "coder",
  "task": "Refactor src/permissions.py to support regex patterns",
  "agent_id": "coder_refactor_1",
  "connect_to": ["researcher_1"]
}
```

- **Known Profile Resolution**: If `role` matches a declared profile under `agents:` (or a recognized role alias such as `code` -> `coder`), the child node inherits that profile's model, temperature, and permitted tool allowlist.
- **Dynamic Profile Fallback**: If an undeclared role is passed, OpenJarvis constructs an agent node with root model defaults and generates a role-tailored persona prompt.

---

## Exit Hierarchy Invariants

1. **Child Lifetime Precedence**: A parent agent cannot exit while any spawned child agents remain in an active state.
2. **Deliverable Publishing**: When a child agent calls `exit_agent`, its output artifact is saved to the content-addressable `ArtifactStore`, and notification envelopes are dispatched to connected neighbors.
3. **Task Completion**: The root coordinator must verify that all child nodes have exited before issuing `complete_task`.
