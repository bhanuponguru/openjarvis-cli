# OpenJarvis

> **Intelligent AI orchestrator with multi-model routing**

OpenJarvis is an AI assistant that routes conversations through specialized language models. Instead of using a single model for everything, OpenJarvis conducts a team of specialists — each optimized for specific domains like mathematics, code generation, knowledge retrieval, and creative writing — then synthesizes their responses into coherent answers.

---

## Why OpenJarvis?

Traditional AI assistants use one model for all tasks. OpenJarvis is different:

- **Smarter routing** — Complex queries automatically chain through the most appropriate specialists
- **Provider flexibility** — Mix and match AI providers (Ollama, OpenAI, Claude, Groq) in a single conversation
- **Production-ready tools** — 29 built-in tools for web search, math, code execution, file operations, and more
- **Full transparency** — See exactly which specialists handled each part of your request
- **Privacy-first option** — Run completely local with Ollama (no cloud dependencies)

---

## Quick Example

```
$ openjarvis

OpenJarvis  (type 'exit' or 'quit' to stop)

> Calculate 15% of Japan's GDP

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → math → tool_use  
  routing: tool_use → math → generalist

Japan's GDP is approximately $4.2 trillion. 
15% of that is $630 billion.
```

Behind the scenes:
1. **Generalist** routes to **knowledge** specialist
2. **Knowledge** uses **web_search** tool to find Japan's GDP
3. **Knowledge** delegates to **math** specialist for calculation
4. **Math** uses **calculate** tool for the percentage
5. **Generalist** synthesizes the final answer

---

## Key Features

### Multi-Model Orchestration

Route conversations through specialized models:

```
User: "Write Python code to solve 2x + 5 = 15"

  routing: generalist → code
  routing: code → math
  routing: math → tool_use
  routing: tool_use → math
  routing: math → code
  routing: code → generalist
```

Each specialist focuses on what it does best.

### Provider Agnostic

Configure each specialist independently to use different AI providers:

- **Ollama** (local, free)
- **OpenAI** (GPT-4, GPT-4o-mini)
- **Groq** (fast inference)
- **Anthropic Claude** (via OpenRouter)

Mix cloud and local models freely in a single conversation.

### 29 Built-In Tools

Production-ready tools that specialists can invoke automatically:

| Category | Tools |
|----------|-------|
| **Web** | Search, fetch URLs, HTTP requests |
| **Math** | Calculate, solve equations, convert units |
| **Files** | Read, write, list, file info |
| **Code** | Execute Python and shell commands |
| **Date/Time** | Get time, calculate dates, format |
| **Text** | Count words, extract JSON, format, replace |
| **System** | Environment variables, system info |
| **Memory** | Save and retrieve notes across conversations |

### Transparent Routing

See the decision-making process in real-time:

```
> Debug this error: TypeError: cannot concatenate 'str' and 'int'

  routing: generalist → code
  routing: code → knowledge

The error occurs when you try to use + between a string and integer.
Use str(number) to convert the integer first: result = "Value: " + str(42)
```

---

## What You Can Do

### Personal Assistant

```
> What's the current time in Tokyo?
> Remind me to call John at 3 PM
> Search for the latest AI research papers
```

### Development Helper

```
> Write a Python function to validate email addresses
> Explain how quicksort works
> Debug this TypeScript error: [paste error]
```

### Research Assistant

```
> What are the latest developments in quantum computing?
> Compare the GDP of the top 5 economies
> Find papers on transformer attention mechanisms
```

### Learning & Education

```
> Teach me how to solve quadratic equations
> Explain async vs sync in JavaScript
> What's the difference between ML and deep learning?
```

---

## How It Works

### The Routing Protocol

OpenJarvis uses simple text-based routing tags:

**Generalist (the conductor):**
- `[ROUTE: return]` — Send this as the final answer
- `[ROUTE: math]` — Route to math specialist
- `[ROUTE: code]` — Route to code specialist
- `[ROUTE: knowledge]` — Route to knowledge specialist

**Specialists:**
- `[RETURN]` — Send back to generalist
- `[DELEGATE: specialist]` — Delegate to another specialist

Tags are automatically stripped from the final output you see.

### Specialist Roles

| Specialist | Purpose | Delegates To |
|-----------|---------|--------------|
| **generalist** | Orchestrator and final synthesis | All specialists |
| **math** | Calculations, proofs, math reasoning | tool_use |
| **code** | Code generation, debugging | math, tool_use |
| **knowledge** | Facts, explanations, research | tool_use |
| **creative** | Writing, brainstorming | — |
| **planning** | Task decomposition | knowledge, math |
| **tool_use** | External tool invocation | — |

### Architecture

```
User Input
    │
    ▼
┌──────────────────────────────┐
│   Generalist (Conductor)     │  Decides: Answer or route?
└──────────────────────────────┘
    │           │           │
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌──────────┐
│  Math  │ │  Code  │ │Knowledge │
└────────┘ └────────┘ └──────────┘
    │           │           │
    ▼           ▼           ▼
┌────────────────────────────────┐
│    Tool Execution Layer        │
└────────────────────────────────┘
    │
    ▼
┌──────────────────────────────┐
│   Generalist Synthesis        │
└──────────────────────────────┘
```

---

## Getting Started

Ready to try OpenJarvis? Here's what's next:

1. **[Install OpenJarvis →](getting-started/installation.md)** — Download and run
2. **[Quick Start Guide →](getting-started/quick-start.md)** — Get up and running in 5 minutes
3. **[Configure Specialists →](configuration/overview.md)** — Set up your AI providers
4. **[Explore Built-in Tools →](tools/overview.md)** — See what OpenJarvis can do

---

## Support & Community

- **Website:** [bhanuponguru.tech/openjarvis](https://bhanuponguru.tech/openjarvis)
- **GitHub:** [github.com/bhanuponguru/OpenJarvis](https://github.com/bhanuponguru/OpenJarvis)
- **Issues:** [Report bugs or request features](https://github.com/bhanuponguru/OpenJarvis/issues)
- **Documentation:** You're reading it!

---

*OpenJarvis — Intelligent AI orchestration, open source and yours.*
