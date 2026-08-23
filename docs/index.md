# OpenJarvis User Manual

> **Intelligent AI Orchestrator with Multi-Model Routing**

OpenJarvis coordinates a team of specialized language models across any OpenAI-compatible API. Instead of relying on one model to handle everything, OpenJarvis routes each part of your conversation to dedicated specialists (such as code, mathematics, factual knowledge, and planning) and executes built-in tools when needed.

---

## Why OpenJarvis?

Traditional AI assistants send all requests to a single model. OpenJarvis enables:

- 🎯 **Specialized Precision**: Direct calculations to a math specialist, programming questions to a code specialist, and research to a knowledge specialist.
- 🔌 **Provider Freedom**: Mix and match Ollama (free & private local models), OpenAI, Groq, OpenRouter, or custom OpenAI-compatible endpoints in one session.
- 🛠️ **29 Production-Ready Built-In Tools**: Automated tools for web searches, math solving, code execution, file I/O, datetime operations, data processing, and session memory.
- 🪄 **Zero-Fuss Onboarding**: First-run interactive setup wizard creates your configuration automatically.
- 🔍 **Full Visibility**: See every routing decision and tool invocation as your request is being processed.

---

## Quick Example

```text
$ openjarvis

oj> Calculate 15% of 80 and write a Python helper function for it

  ↳ routing: generalist → math
  ⚙ tool: evaluate_expression {"expression": "0.15 * 80"}
    → 12.0
  ↳ routing: math → code

15% of 80 is **12.0**.

Here is a Python function to calculate percentage values:

```python
def calculate_percentage(part_percent: float, total: float) -> float:
    """Calculate the given percentage of a total value."""
    return (part_percent / 100.0) * total
```
```

---

## Key Capabilities

### 1. Multi-Model Orchestration
The **generalist** coordinates conversations, deciding whether to answer directly or route to a specialist. Specialists complete their domain task, call required tools, and return results to synthesize a final answer.

### 2. Built-In Tools Suite (29 Tools)

| Category | Count | Highlight Capabilities |
| :--- | :--- | :--- |
| **[Date & Time](tools/datetime.md)** | 4 | ISO timestamps, timezone conversions, date arithmetic, days between dates |
| **[Math](tools/math.md)** | 4 | Safe expression evaluation, unit conversions, algebraic equation solving, prime factorization |
| **[File I/O](tools/files.md)** | 6 | Read/write text files, directory listing, regex search across files, file metadata |
| **[Web](tools/web.md)** | 3 | Web search via DuckDuckGo, web page text extraction, Wikipedia lookups |
| **[Code Execution](tools/code.md)** | 3 | Sandboxed subprocess Python execution, shell command execution, Python syntax linting |
| **[Data Processing](tools/data.md)** | 5 | JSON pretty-printing, jq-style dot queries, CSV table formatting, regex search/replace |
| **[Session Memory](tools/memory.md)** | 4 | Store notes, recall notes, list keys, and delete session notes |

### 3. Provider Agnostic
Configure each specialist to point to different endpoints, models, temperatures, and timeouts in your `specialists.yaml` file.

---

## Next Steps

1. **[Installation Guide →](getting-started/installation.md)** — Download pre-built binaries or install from source
2. **[Quick Start Guide →](getting-started/quick-start.md)** — Run the setup wizard and start chatting
3. **[Configuration Overview →](configuration/overview.md)** — Learn the `specialists.yaml` format
4. **[Built-in Tools Manual →](tools/overview.md)** — Explore all 29 tools in detail
5. **[Command-Line Usage →](usage/cli.md)** — Terminal shortcuts and REPL commands

