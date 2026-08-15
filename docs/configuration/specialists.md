# Specialists Configuration

Specialists are the domain-specific models that OpenJarvis routes requests to. The generalist acts as conductor, deciding which specialist handles each part of a query.

---

## The Generalist

The generalist is required and acts as the conductor for every conversation. It receives all user input, decides whether to answer directly or route to a specialist, and synthesizes the final response.

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis, an intelligent AI assistant.
    
    For each user request, decide how to respond:
    - Answer directly for simple questions
    - Route to specialists for complex or domain-specific tasks
    
    Routing tags (use on their own line):
    [ROUTE: return]     — Send this response directly to the user
    [ROUTE: math]       — Route to math specialist
    [ROUTE: code]       — Route to code specialist
    [ROUTE: knowledge]  — Route to knowledge specialist
    [ROUTE: tool_use]   — Route to tool specialist
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7
```

### Generalist System Prompt Rules

The generalist's system prompt must include:

1. **Its role** — What it is and what it does
2. **Routing instructions** — Which tags to use and when
3. **All available specialists** — Listed so it knows what to route to

The routing tag format is `[ROUTE: specialist_name]` where `specialist_name` matches a key under `specialists:` in your config, or `return` to send the response directly to the user.

---

## Specialists

Specialists handle specific domains. Each specialist must:

1. Know its domain (from `system_prompt`)
2. Know how to return results (`[RETURN]` tag)
3. Optionally know how to delegate further (`[DELEGATE: name]`)

### Minimal Specialist

```yaml
specialists:
  math:
    system_prompt: |
      You are a mathematics specialist.
      Solve problems step-by-step, showing your work.
      When done, end your response with [RETURN] on its own line.
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

### Specialist with Tool Access

```yaml
specialists:
  math:
    system_prompt: |
      You are a mathematics specialist.
      You can use the calculate tool for arithmetic.
      Show your work, then end with [RETURN].
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
    delegates_to: ["tool_use"]
```

### Specialist with Peer Delegation

```yaml
specialists:
  code:
    system_prompt: |
      You are a code specialist.
      For math problems within code, delegate to math: [DELEGATE: math]
      For tool use, delegate to tool_use: [DELEGATE: tool_use]
      When done, end with [RETURN].
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]
```

---

## Built-in Specialist Roles

These are the commonly used specialist names. You can use any names you want, but these are well-understood conventions:

| Name | Purpose | Recommended Model |
|------|---------|-------------------|
| `math` | Calculations, proofs, equations | Any capable model, low temperature |
| `code` | Code generation, debugging, review | Code-specific model (codellama, deepseek-coder) |
| `knowledge` | Facts, research, explanations | General capable model |
| `creative` | Writing, brainstorming, storytelling | Higher temperature model |
| `planning` | Task decomposition, step-by-step plans | General capable model |
| `tool_use` | Executes tools (web search, calculations, etc.) | Any model with good instruction following |

The `tool_use` specialist is special — it's the gateway to OpenJarvis's 29 built-in tools. Specialists that need tools must `delegates_to: ["tool_use"]`.

---

## System Prompt Engineering

### Generalist Routing Prompts

The generalist's routing instructions determine how intelligently it delegates. A good routing prompt:

```yaml
system_prompt: |
  You are OpenJarvis, an intelligent AI assistant.
  
  Think carefully before routing. For each request:
  - Simple questions or explanations → answer directly with [ROUTE: return]
  - Math, equations, calculations → [ROUTE: math]
  - Code, programming, debugging → [ROUTE: code]
  - Facts, research, current events → [ROUTE: knowledge]
  - Creative writing, stories, poetry → [ROUTE: creative]
  - Multi-step planning → [ROUTE: planning]
  
  You can route to multiple specialists sequentially by routing, 
  receiving the result, then routing again.
  
  Always synthesize a final answer with [ROUTE: return] when done.
```

### Specialist Return Prompts

Specialists must know to return. A good specialist system prompt:

```yaml
system_prompt: |
  You are a mathematics specialist. Your job is to solve math problems accurately.
  
  - Show your work step by step
  - Use exact values when possible (fractions, not decimals)
  - If a calculation is needed, use the calculate tool
  - If the problem requires knowledge (like GDP of a country), return to generalist
  
  Always end your response with [RETURN] on its own line.
```

### Common Mistakes

**Missing `[RETURN]` in specialist prompt:**
The specialist will keep responding without returning to the generalist. Always include `[RETURN]` instructions.

**Too many routing options:**
The generalist gets confused if given 10+ specialists. Start with 3-4 and add more as needed.

**No routing tags in generalist:**
If the generalist's system prompt doesn't mention routing tags, it won't use them and will answer everything directly.

---

## Delegation Graph

Delegation defines which specialists can talk to each other. Only the paths you define are allowed:

```yaml
specialists:
  math:
    delegates_to: ["tool_use"]           # math → tool_use

  code:
    delegates_to: ["math", "tool_use"]   # code → math, code → tool_use

  knowledge:
    delegates_to: ["tool_use"]           # knowledge → tool_use

  tool_use:
    delegates_to: []                     # tool_use returns to whoever called it
```

This creates:
```
generalist → math → tool_use
generalist → code → math → tool_use
generalist → code → tool_use
generalist → knowledge → tool_use
```

If a specialist tries to delegate to a name not in its `delegates_to` list, the delegation is ignored.

---

## Minimal Configuration

The absolute minimum configuration — just the generalist:

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Answer questions helpfully.
    End responses with [ROUTE: return].
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  temperature: 0.7
```

With no specialists defined, the generalist handles everything directly.

---

## See Also

- [Configuration Overview](overview.md) — All configuration fields explained
- [Providers](providers.md) — Provider-specific setup
- [Routing Protocol](../usage/routing.md) — How routing tags work
