# Specialists Configuration

Specialists are domain-specific language model roles configured to handle distinct types of tasks (such as writing code, solving mathematics, answering factual questions, or decomposing complex plans).

The **generalist** coordinates the team, while **specialists** execute tasks, call built-in tools as needed, and either return answers or delegate to peer specialists.

---

## The Generalist (Router & Conductor)

The `generalist` role is required for all configurations. It receives user prompts, decides whether to answer directly or route to a domain specialist, and synthesizes the final answer.

```yaml
generalist:
  name: "generalist"
  system_prompt: |
    You are the ROUTER of OpenJarvis. Choose the best specialist for each query:
    [ROUTE: math]       - Calculations, proofs, algebra, numerical problems
    [ROUTE: code]       - Software development, debugging, scripting
    [ROUTE: knowledge]  - Factual questions, concepts, general research
    [ROUTE: return]     - Answer directly or deliver tool result
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0
```

### Generalist Prompt Guidelines

1. **Explicit Routing Tags**: List each specialist tag (`[ROUTE: <specialist>]`) clearly on its own line.
2. **Direct Answer Tag**: Specify `[ROUTE: return]` when the query does not need specialist delegation.
3. **Low Temperature**: Set `temperature: 0.0` or `0.1` so the router makes reliable, deterministic decisions.

---

## Defining Specialists

Under the `specialists:` section, define custom specialist roles. Each specialist is configured with its own system prompt, model endpoint, temperature, and optional delegation targets:

```yaml
specialists:
  math:
    name: "math"
    system_prompt: |
      You are the MATH specialist.
      Solve calculations, algebra, and quantitative problems step-by-step.
      You have access to calculation and equation-solving tools via function calling.
      End your final answer with [RETURN].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: []

  code:
    name: "code"
    system_prompt: |
      You are the CODE specialist.
      Write, analyze, and debug software.
      You have access to file and code execution tools via function calling.
      If you require deep mathematical derivations, emit [DELEGATE: math].
      Otherwise, end your response with [RETURN].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]

  planning:
    name: "planning"
    system_prompt: |
      You are the PLANNING specialist.
      Decompose complex, multi-step tasks into clear, ordered action items.
      If you need factual checks, emit [DELEGATE: knowledge].
      If you need quantitative estimations, emit [DELEGATE: math].
      Otherwise, end your completed plan with [RETURN].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: ["knowledge", "math"]
```

---

## Tool Access for Specialists

All 29 built-in tools (web search, math solving, file I/O, code execution, datetime, data parsing, session memory) are provided directly to models via standard OpenAI function calling.

Models call tools automatically whenever their prompt requires it. Results are executed by OpenJarvis and fed back into the model conversation before the specialist emits `[RETURN]`.

---

## Peer Delegation Rules (`delegates_to`)

The `delegates_to` field defines which other specialists a specialist is allowed to call:

```yaml
specialists:
  code:
    delegates_to: ["math"] # code can delegate to math
  planning:
    delegates_to: ["knowledge", "math"] # planning can delegate to knowledge or math
```

- **Allowed Target**: If a specialist emits `[DELEGATE: math]` and `"math"` is in its `delegates_to` list, OpenJarvis transitions execution to the `math` specialist.
- **Unapproved Target**: If a specialist attempts to delegate to an unlisted specialist, OpenJarvis safely intercepts the request and routes back to the generalist to recover.

---

## Common Specialist Roles

| Role | Domain Focus | Recommended Settings |
| :--- | :--- | :--- |
| **`math`** | Arithmetic, algebra, statistics, equations | Temperature `0.0`, high precision |
| **`code`** | Software architecture, algorithms, bug fixes | Temperature `0.0`, code-tuned models (e.g. `codellama`, `gpt-4o`) |
| **`knowledge`** | Research, explanations, current facts | Temperature `0.2` - `0.4`, web tools enabled |
| **`creative`** | Brainstorming, copywriting, fiction | Temperature `0.7` - `0.9` |
| **`planning`** | Project roadmap, step-by-step decomposition | Temperature `0.2`, delegates to `knowledge` & `math` |

---

## Next Steps

- **[Providers Guide →](providers.md)** — Connect Ollama, OpenAI, Groq, or OpenRouter
- **[Built-in Tools Reference →](../tools/overview.md)** — List of all 29 tools available to specialists
- **[Routing Protocol →](../usage/routing.md)** — Detailed mechanics of routing tags and return tokens
