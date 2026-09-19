# Specialists Configuration

Specialists are domain-specific language model roles configured to handle distinct types of tasks (such as writing code, solving mathematics, answering factual questions, or decomposing complex plans).

The **generalist** coordinates the team, while **specialists** execute tasks, call permitted tools as needed, and either return answers or delegate to peer specialists.

---

## Declarative Prompts & Harness Templating

OpenJarvis uses **internal harness prompt templating**. You no longer need to write manual routing tags (`[ROUTE: ...]`, `[DELEGATE: ...]`, or `[RETURN]`) in your system prompts.

Your configuration only needs to declare:
1. **Domain functionality & boundaries**: What the specialist does and what it refuses.
2. **Delegation targets (`delegates_to`)**: Which peer specialists it is permitted to delegate to.
3. **Tool permissions (`tools`)**: Which tools the specialist is allowed to access (optional).

At runtime, the OpenJarvis harness dynamically injects the standardized routing protocol, active specialists directory, and completion contracts into the system prompt.

---

## The Generalist (Router & Conductor)

The `generalist` role is required for all configurations. It receives user prompts, decides whether to answer directly or route to a domain specialist, and synthesizes the final answer.

```yaml
generalist:
  name: "generalist"
  description: "Router and coordinator managing task dispatch and final answer synthesis."
  system_prompt: |
    You are the router and coordinator of OpenJarvis.
    Your responsibility is to analyze incoming user requests and dispatch them to the most qualified specialist.
    Under no circumstances should you solve domain-specific mathematical problems, write software code, conduct deep research, compose creative fiction, or build execution roadmaps yourself.
    Coordinate execution across your specialist team, and synthesize clear, helpful responses when specialists return their work.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0
```

### Generalist Guidelines
- **Pure Role Definition**: Focus instructions on dispatching tasks and synthesizing final answers.
- **Negative Constraints**: Instruct the router not to execute domain tasks directly when specialists are available.
- **Low Temperature**: Set `temperature: 0.0` or `0.1` so routing decisions are deterministic and reliable.

---

## Defining Specialists with Domain Boundaries

Under the `specialists:` section, define custom specialist roles:

```yaml
specialists:
  math:
    name: "math"
    description: "Calculations, arithmetic, algebra, calculus, equations, statistics, quantitative reasoning, and numerical proofs."
    system_prompt: |
      You are the MATH specialist of OpenJarvis.
      Your sole job is to solve mathematics, calculations, numerical equations, formal proofs, statistics, and quantitative reasoning.
      Focus purely on rigorous, clear mathematical derivations and solutions.
      Act only on mathematical and quantitative tasks. Leave software code, factual research, creative writing, and project planning to their respective specialists.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["code"]
    tools:
      - "calculator"
      - "evaluate_expression"
      - "solve_linear_equation"
      - "solve_quadratic_equation"
      - "convert_units"
      - "compute_statistics"

  code:
    name: "code"
    description: "Software engineering, writing, analyzing, debugging, reviewing, refactoring code, algorithms, and technical architecture."
    system_prompt: |
      You are the CODE specialist of OpenJarvis.
      Your sole job is software engineering: writing, analyzing, debugging, reviewing, refactoring, and explaining computer software, technical architecture, algorithms, and data structures.
      Act only on programming, scripting, and software engineering tasks.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]
    tools:
      - "str_replace_editor"
      - "bash"
      - "execute_python"
      - "lint_python_code"
      - "git_status"
      - "git_diff"
      - "git_log"
      - "git_show"

  creative:
    name: "creative"
    description: "Fiction, storytelling, poetry, creative writing, metaphors, and stylistic rewrites."
    system_prompt: |
      You are the CREATIVE specialist of OpenJarvis.
      Your sole job is creative writing: storytelling, narrative development, poetry, metaphorical explorations, creative copywriting, and stylistic rewriting.
      Deliver imaginative, stylistically refined output matching the requested tone.
    provider: "openai"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.8
    delegates_to: []
    tools: []
```

---

## Per-Specialist Tool Access Control

By default, specialists have access to all registered built-in tools. For greater control, safety, and token efficiency, you can configure explicit tool access per specialist using the optional `tools` field:

- **Omitted or `null`**: The specialist has access to all registered tools (default).
- **`tools: []`**: Pure reasoning agent with zero tool access. No tools are bound to the model, preventing tool hallucinations or accidental execution.
- **`tools: ["tool_a", "tool_b"]`**: The specialist is strictly restricted to the specified tools. Only these tools are included in the model's function schema, and execution of any unpermitted tool is automatically blocked with permission errors.

### Scoped Tool RAG

When Two-Phase Tool Retrieval (RAG) is enabled:

```yaml
tool_retrieval:
  enabled: true
  top_k: 5
```

OpenJarvis dynamically performs semantic similarity search **only across the tools permitted to the active specialist**. Tools outside the specialist's `tools` list are never indexed, scored, or retrieved for that specialist.

---

## Delegation Rules (`delegates_to`)

The `delegates_to` list declares which peer specialists a specialist is allowed to invoke.

- If `delegates_to: ["code"]`, the harness teaches the specialist how to delegate subtasks to `code` using `[DELEGATE: code]`.
- If a model attempts to delegate to an unpermitted target, the conductor intercepts the call and safely redirects back to the generalist for recovery.
- If `delegates_to: []`, the harness only instructs the specialist on task completion (`[RETURN]`).
