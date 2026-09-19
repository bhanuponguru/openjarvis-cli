# Advanced Configuration

This page covers power-user configuration techniques, environment management, and specialized setups for OpenJarvis.

---

## Managing Multiple Configurations

You can maintain different specialist configurations for different tasks (e.g. coding, research, writing):

```text
~/.config/openjarvis/
├── specialists.yaml  # Default setup
├── coding.yaml       # Code-focused specialists (low temp, local code models)
└── research.yaml     # Research setup (high-capacity models, web search)
```

To run OpenJarvis with a specific configuration:

```bash
OJ_CONFIG=~/.config/openjarvis/coding.yaml openjarvis
```

---

## Per-Project Configuration

You can place a `specialists.yaml` file in the root of any project directory. When you run `openjarvis` inside that directory, it automatically loads `./specialists.yaml` before falling back to your user config.

```text
my-web-app/
├── specialists.yaml  # Custom specialists for this codebase
├── package.json
└── src/
```

---

## Environment Variable Management

All API credentials are read from environment variables defined by `api_key_env` in your configuration:

```yaml
generalist:
  api_key_env: "OPENAI_API_KEY"

specialists:
  knowledge:
    api_key_env: "GROQ_API_KEY"
```

### Setting Credentials

Export variables in your active shell or shell profile:

```bash
# ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-..."
```

---

## Offline / Air-Gapped Setup

For completely offline, air-gapped environments, configure OpenJarvis with Ollama:

```yaml
max_hops: 8

generalist:
  system_prompt: |
    You are OpenJarvis.
    Route requests using:
    [ROUTE: math] - Math problems
    [ROUTE: code] - Programming tasks
    [ROUTE: return] - Final answer
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  temperature: 0.0

specialists:
  math:
    system_prompt: "You are the math specialist. Solve step-by-step. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.0
    delegates_to: []

  code:
    system_prompt: "You are the code specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.0
    delegates_to: []
```

> **Offline Tool Behavior**: When offline, local tools (math evaluation, file operations, date/time calculations, data parsing, and code execution) work fully. Web search (`search_web`) and URL fetching (`fetch_url`) require an active internet connection.

---

## Per-Specialist Tool Permissions & Scoped Tool RAG

Advanced users can restrict tool access per specialist using the `tools` list:

```yaml
specialists:
  math:
    system_prompt: "You are the math specialist."
    # Allow math specialist ONLY mathematical tools
    tools:
      - "calculator"
      - "evaluate_expression"
      - "solve_linear_equation"
      - "solve_quadratic_equation"

  creative:
    system_prompt: "You are the creative writer."
    # Pure reasoning agent: no tools exposed or callable
    tools: []

  system_admin:
    system_prompt: "You are the system administrator."
    # Unrestricted access to all tools (default behavior)
    tools: null
```

### Defense-in-Depth Enforcement
1. **Context Scoping**: Only permitted tools are serialized into the model's function-calling tool schema.
2. **Scoped Tool RAG**: If Two-Phase Tool Retrieval is enabled (`tool_retrieval.enabled: true`), semantic retrieval and always-on tool injection are strictly evaluated *only* against the specialist's permitted tools.
3. **Execution Guard**: If a model generates a hallucinated or unpermitted tool call, OpenJarvis intercepts and rejects execution with a security block event before any code or tool runs.

---

## Fine-Tuning Performance & Timeouts

### Temperature per Domain
- **Deterministic Tasks (`0.0` - `0.1`)**: Math calculations, symbolic algebra, code generation, JSON transformation.
- **Balanced Reasoning (`0.2` - `0.4`)**: Generalist orchestration, factual summaries, planning.
- **Creative Generation (`0.7` - `0.9`)**: Ideation, storytelling, brainstorming.

### Request Timeouts
The default per-request timeout is `60.0` seconds. For slower local models or deep reasoning queries, increase the timeout:

```yaml
specialists:
  math:
    timeout: 120.0 # 2 minutes
```

---

## See Also

- [Configuration Overview](overview.md) — All configuration fields
- [Specialists Guide](specialists.md) — Specialist prompt engineering
- [Providers Guide](providers.md) — Provider-specific setup
- [Troubleshooting](../troubleshooting.md) — Common issues and fixes
