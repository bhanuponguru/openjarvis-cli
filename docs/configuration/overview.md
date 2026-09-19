# Configuration Overview

OpenJarvis uses a simple YAML configuration file (typically `specialists.yaml`) to define the orchestrator and domain specialists.

---

## Configuration File Discovery Order

When you run `openjarvis`, the CLI automatically locates your configuration using this search order:

1. **`OJ_CONFIG` environment variable** (highest priority):
   ```bash
   export OJ_CONFIG=/path/to/my-config.yaml
   openjarvis
   ```
2. **Current working directory**: `./specialists.yaml`
3. **User configuration directory**: `~/.config/openjarvis/specialists.yaml`
4. **System-wide configuration**: `/etc/openjarvis/specialists.yaml` (Linux / macOS)

If no configuration file is found in any location, OpenJarvis launches the **interactive setup wizard** to create one for you.

---

## Configuration Structure

A complete configuration defines the global hop cap, the required `generalist` orchestrator, and optional domain `specialists`:

```yaml
max_hops: 10 # Maximum specialist transitions per query

generalist:
  name: "generalist"
  description: "Primary orchestrator and router."
  system_prompt: |
    You are the router and coordinator of OpenJarvis.
    Analyze user requests, route domain-specific tasks to qualified specialists,
    and synthesize final responses when specialists return their work.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0
  timeout: 60.0

specialists:
  math:
    name: "math"
    description: "Calculations, arithmetic, algebra, equations, and statistics."
    system_prompt: |
      You are the MATH specialist. Solve mathematics and quantitative problems with rigor.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["code"]
    tools: ["calculator", "evaluate_expression", "solve_linear_equation"]

  code:
    name: "code"
    description: "Software engineering, writing, analyzing, and debugging code."
    system_prompt: |
      You are the CODE specialist. Write, inspect, and debug software.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]
    tools: ["str_replace_editor", "bash", "execute_python"]

  knowledge:
    name: "knowledge"
    description: "Factual concepts, historical research, and general definitions."
    system_prompt: |
      You are the KNOWLEDGE specialist. Answer factual questions and explain concepts.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: []
    tools: ["fetch_webpage", "search_web", "query_wikipedia"]
```

---

## Field Reference

### Global Settings

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `max_hops` | Integer | `10` | Maximum number of model hops allowed for a single prompt to prevent infinite delegation loops. |

### Specialist Settings (`generalist` and each `specialists` entry)

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `system_prompt` | String | **Required** | Functional instructions defining role and domain boundaries. Routing protocols are injected automatically. |
| `name` | String | Section key | Identifier for this role (e.g. `generalist`, `math`, `code`). |
| `description` | String | `null` | Optional concise summary of role expertise, provided to the generalist router for intelligent dispatching. |
| `provider` | String | `"openai"` | Provider protocol (all OpenAI-compatible endpoints use `"openai"`). |
| `base_url` | String | `"http://localhost:11434/v1"` | The HTTP base URL of the API endpoint. |
| `model` | String | `"llama3"` | Model name requested from the provider. |
| `api_key_env` | String | `null` | Name of the environment variable holding the API key (e.g. `"OPENAI_API_KEY"`). |
| `temperature` | Float | `0.7` | Sampling temperature (0.0 for deterministic, 1.0 for creative). |
| `max_tokens` | Integer | `null` | Optional max tokens to generate. If omitted, no limit is sent. |
| `stop` | List[String] | `[]` | Optional list of stop sequences. |
| `timeout` | Float | `60.0` | HTTP request timeout in seconds. |
| `delegates_to` | List[String] | `[]` | List of specialist names this specialist is permitted to delegate to. |
| `tools` | List[String] | `null` | Optional allowlist of permitted tool names. If `null`, inherits all available tools. If `[]`, pure reasoning agent (0 tools). |

---

## Configuration Recipes

### 1. Completely Local & Free with Ollama
```yaml
generalist:
  system_prompt: "You are OpenJarvis. Route using [ROUTE: math], [ROUTE: code], or [ROUTE: return]."
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  temperature: 0.0

specialists:
  math:
    system_prompt: "You are the math specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.0

  code:
    system_prompt: "You are the code specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.0
```

### 2. High-Speed Hybrid Setup
```yaml
generalist:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0

specialists:
  knowledge:
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.2

  math:
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.0
```

---

## Validation & Startup Checks

OpenJarvis validates your configuration when starting:
- **Unknown Keys**: Reports the exact line/section and lists allowed keys if a typo occurs.
- **Missing Prompts**: Flags missing required `system_prompt` entries immediately.
- **Invalid Delegation**: Ensures all `delegates_to` names exist in the `specialists` map.
- **Missing API Keys**: Alerts you with the environment variable name if an API key is missing.

---

## Next Steps

- **[Specialists Guide →](specialists.md)** — Designing specialist prompts and delegation
- **[Providers Guide →](providers.md)** — Setting up Ollama, OpenAI, Groq, and OpenRouter
- **[Advanced Options →](advanced.md)** — Fine-tuning timeouts, temperatures, and hop limits

