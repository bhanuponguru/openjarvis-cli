# Agents & Profiles Configuration

OpenJarvis models every node in the Multi-Agent System (MAS) as an autonomous **Conductor** instance. Agents are declared under the `agents:` section in your configuration, alongside the top-level `root_agent:`.

---

## Agent Configuration Schema

Each agent profile specifies its identity, persona, execution limits, and scoped access to tools and specialists:

```yaml
agents:
  <agent_name>:
    name: "<agent_name>"            # Unique identifier / role label
    role: "<role>"                  # Functional role (e.g. researcher, coder, math, planner)
    description: "..."              # Human-readable summary of capability
    system_prompt: |                # Instruction set defining mission, behavior, and boundaries
      You are the ...
    provider: "openai"              # LLM provider (openai, anthropic, google, ollama, custom)
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    api_key_env: "OPENAI_API_KEY"   # Environment variable holding API key
    temperature: 0.0                # Temperature (0.0 for deterministic, higher for creative)
    timeout: 60.0                   # Per-request timeout in seconds
    max_hops: 10                    # Hop limit for this agent's internal Conductor
    tools:                          # Scoped tool list (null for full registry access)
      - "str_replace_editor"
      - "bash"
      - "execute_python"
    allowed_specialists:            # Scoped domain specialists for inner delegation
      - "math"
```

---

## Canonical Agent Profiles

OpenJarvis ships with four standard pre-configured agent profiles:

### 1. Researcher (`researcher`)
- **Role**: Factual verification, academic literature search, documentation retrieval.
- **Default Tools**: `fetch_webpage`, `search_web`, `query_wikipedia`.
- **Mission**: Ingests external web data, summarizes findings, and reports them to neighbor agents.

### 2. Coder (`coder`)
- **Role**: Software engineering, testing, debugging, architecture, refactoring.
- **Default Tools**: `str_replace_editor`, `bash`, `execute_python`, `lint_python_code`, `git_status`, `git_diff`.
- **Mission**: Writes, inspects, and verifies code; produces software deliverables as artifacts upon exit.

### 3. Math Specialist (`math`)
- **Role**: Formal derivations, quantitative reasoning, arithmetic, statistical analysis.
- **Default Tools**: `calculator`, `evaluate_expression`, `solve_linear_equation`, `solve_quadratic_equation`, `convert_units`, `compute_statistics`.
- **Mission**: Solves numeric problems with symbolic precision and shares mathematical derivations.

### 4. Planner (`planner`)
- **Role**: High-level task decomposition, critical path analysis, dependency graphs.
- **Default Tools**: `get_current_time`, `calculate_date_difference`.
- **Mission**: Decomposes complex user goals into sub-tasks for sibling agents to execute.

---

## Dynamic Runtime Agents

In addition to static profiles declared in `.openjarvis/config.yaml`, the Root Agent (and intermediate agents) can dynamically instantiate custom agents at runtime using the `spawn_agent` tool:

```json
{
  "role": "auditor",
  "task": "Audit src/security.py for potential SQL and command injections",
  "agent_id": "security_auditor_1"
}
```

If the role matches a declared profile in `agents:`, the spawned agent inherits that profile's configurations. If an undeclared role is requested, OpenJarvis automatically constructs a custom Conductor with a dedicated persona prompt matching the assignment.

