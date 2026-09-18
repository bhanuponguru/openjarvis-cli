# OpenJarvis User Manual

> **Intelligent AI Orchestrator with Multi-Model Routing**

OpenJarvis coordinates a team of specialized language models across any OpenAI-compatible API. Instead of relying on one model to handle everything, OpenJarvis routes each part of your conversation to dedicated specialists (such as code, mathematics, factual knowledge, and planning) and executes built-in tools when needed.

---

## Why OpenJarvis?

Traditional AI assistants send all requests to a single model. OpenJarvis enables:

- 🎯 **Specialized Precision**: Direct calculations to a math specialist, programming questions to a code specialist, and research to a knowledge specialist.
- 🔌 **Provider Freedom**: Mix and match Ollama (free & private local models), OpenAI, Anthropic, Gemini, Groq, or custom OpenAI-compatible endpoints in one session.
- 🛠️ **49 Production-Ready Built-In Tools**: Automated tools for file inspection, Git/patch management, web requests, code execution, AST math solving, SQLite queries, datetime operations, and persistent memory.
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

### 2. Built-In Tools Suite (49 Tools Across 9 Modules)

| Category | Count | Highlight Capabilities |
| :--- | :--- | :--- |
| **[File I/O](tools/files.md)** | 9 | Read/write files, recursive directory search, file regex match, glob locator, delete file |
| **[Git & Version Control](tools/git.md)** | 4 | Unified git diff inspection, short status summary, commit log history, patch application |
| **[Web & API](tools/web.md)** | 5 | Web search via DuckDuckGo, web page text extraction, Wikipedia lookups, REST HTTP, OpenAPI parsing |
| **[Code Execution](tools/code.md)** | 4 | Sandboxed Python execution, shell commands, syntax linting, pytest test suite runner |
| **[Code Editor & Terminal](tools/editor.md)** | 3 | Atomic string replacement editor with undo history, bash command execution |
| **[Data Processing](tools/data.md)** | 6 | JSON pretty-printing, jq queries, CSV table formatting, regex search/replace, SQLite querying |
| **[Math & Arithmetic](tools/math.md)** | 4 | Safe expression evaluation, unit conversions, algebraic equation solving, prime factorization |
| **[Date & Time](tools/datetime.md)** | 4 | ISO timestamps, timezone conversions, date arithmetic, days between dates |
| **[Session & Memory](tools/memory.md)** | 10 | Save/read/search persistent memories, session notes storage with backwards compatibility |

### 3. Provider Agnostic
Configure each specialist to point to different endpoints, models, temperatures, and timeouts in your `specialists.yaml` file.

---

## Next Steps

1. **[Installation Guide →](getting-started/installation.md)** — Install via `uvx`, `uv tool`, `pip`, pre-built binaries, or source
2. **[Quick Start Guide →](getting-started/quick-start.md)** — Run the setup wizard and start chatting
3. **[Configuration Overview →](configuration/overview.md)** — Learn the `specialists.yaml` format
4. **[Built-in Tools Manual →](tools/overview.md)** — Explore all 49 tools in detail
5. **[Command-Line Usage →](usage/cli.md)** — Terminal shortcuts, CLI flags, and REPL commands


