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
    You are the ROUTER and DISPATCHER of OpenJarvis.
    Your SOLE responsibility is to analyze the user request and route to the best specialist.
    CRITICAL: Do NOT attempt to solve specialized domain tasks yourself.
    Route strictly using exactly ONE tag on its own line at the end:
    - [ROUTE: math] for calculations, algebra, equations, and statistics
    - [ROUTE: code] for programming, debugging, algorithms, and software engineering
    - [ROUTE: knowledge] for factual questions, research, and concept explanations
    - [ROUTE: return] ONLY for basic conversational greetings or delivering the final synthesis.
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
4. **Hard Non-Solving Constraint**: Strongly instruct the router NOT to attempt solving domain tasks directly.

---

## Defining Specialists with Hard Role Boundaries

Under the `specialists:` section, define custom specialist roles. To prevent specialists from "answering everything" and stepping outside their expertise, system prompts should strictly enforce domain boundaries and explicit negative constraints:

```yaml
specialists:
  math:
    name: "math"
    system_prompt: |
      You are EXCLUSIVELY the MATH specialist of OpenJarvis.
      Your SOLE job is to solve mathematics, calculations, numerical equations, formal proofs, and statistics.
      STRICT BOUNDARIES: Act ONLY on mathematical and quantitative tasks.
      Do NOT write software application code, do NOT answer general trivia or history, and do NOT engage in casual conversation.
      Focus strictly on mathematical derivation. You MUST end your response with [RETURN].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: []

  code:
    name: "code"
    system_prompt: |
      You are EXCLUSIVELY the CODE specialist of OpenJarvis.
      Your SOLE job is software engineering: writing, analyzing, debugging, and explaining code, architecture, and algorithms.
      STRICT BOUNDARIES: Act ONLY on programming tasks. Do NOT perform non-programming domain tasks, essays, or trivia.
      For complex manual math derivations, delegate to math using [DELEGATE: math].
      Focus strictly on programming. End your response with [RETURN] or [DELEGATE: math].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]

  planning:
    name: "planning"
    system_prompt: |
      You are EXCLUSIVELY the PLANNING specialist of OpenJarvis.
      Your SOLE job is task decomposition and workflow planning: breaking down complex objectives into structured, sequential, actionable roadmaps.
      STRICT BOUNDARIES: Do NOT execute the tasks yourself (do not write code or perform heavy calculations).
      Delegate factual questions to knowledge with [DELEGATE: knowledge] and math to math with [DELEGATE: math].
      End your completed plan with [RETURN].
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: ["knowledge", "math"]
```

---

## Tool Access for Specialists

All 49 built-in tools (file inspection, Git & patch tools, web search, REST requests, code execution, AST math solving, SQLite querying, datetime, and persistent memory) are provided directly to models via standard OpenAI function calling.

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
- **[Built-in Tools Reference →](../tools/overview.md)** — List of all 49 tools available to specialists
- **[Routing Protocol →](../usage/routing.md)** — Detailed mechanics of routing tags and return tokens
