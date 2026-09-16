# OpenJarvis — Multi-Model AI Orchestrator

OpenJarvis is an intelligent AI orchestrator and interactive terminal assistant. Instead of relying on a single model for all tasks, OpenJarvis coordinates a team of specialist AI models (for coding, mathematics, factual knowledge, and planning) and 29 built-in tools over any OpenAI-compatible API.

---

## Features

- 🎯 **Intelligent Multi-Model Routing**: Routes user requests to domain specialists and synthesizes clear, unified answers.
- 🔌 **Provider Agnostic**: Connects to Ollama (local and private), OpenAI, Groq, OpenRouter, Claude, or any OpenAI-compatible API.
- 🛠️ **31 Production-Ready Built-In Tools**: Automated function-calling tools for web search, math calculations, code execution, file I/O, datetime operations, data parsing, session notes, and native SWE tools (`str_replace_editor`, `execute_bash`).
- 🪄 **Interactive Setup Wizard**: Automatically configures your model providers on first run if no configuration file exists.
- 💻 **Modern Terminal Interface**: Interactive REPL with syntax-highlighted Markdown rendering, multiline input, command history, and real-time routing status.
- 🚀 **Standalone Executables**: Zero Python runtime required when using pre-built binary releases.

---

## Quick Start

### 1. Installation

#### Standalone Binary (Recommended)
Download the binary for your platform from [Releases](https://github.com/bhanuponguru/OpenJarvis/releases):

```bash
# Linux / macOS
tar xzf openjarvis-*.tar.gz
cd openjarvis-*
./openjarvis

# Windows
# Extract the ZIP archive and run openjarvis.exe
```

#### From Source (Python 3.13+)
```bash
git clone https://github.com/bhanuponguru/OpenJarvis.git
cd OpenJarvis
uv sync --all-packages
uv run openjarvis
```

### 2. First Run & Setup Wizard

When you launch `openjarvis` without an existing configuration, an interactive wizard prompts you to set up your preferred provider:

```text
════════ OpenJarvis Setup ════════

Welcome! No specialists.yaml config was found.
Let's create one so you can start using OpenJarvis.

Step 1/3 — Choose your LLM provider
  ollama     — Local models via Ollama (free, private)
  openai     — OpenAI API (GPT-4o, etc.)
  anthropic  — Anthropic API (Claude 3.5 Sonnet, etc.)
Model name [llama3]: 

Step 2/3 — Where to save the config
✓ Config written to ~/.config/openjarvis/specialists.yaml

oj> 
```

### 3. Interactive Usage

Type prompts naturally into the OpenJarvis prompt:

```text
oj> What's 15% of 80, and write a Python helper function for it?

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

To exit the interactive session, type `exit`, `quit`, or press `Ctrl+C` / `Ctrl+D`.

---

## Configuration Guide

OpenJarvis searches for its configuration in the following priority order:
1. `OJ_CONFIG` environment variable (`export OJ_CONFIG=/path/to/specialists.yaml`)
2. `./.openjarvis/config/specialists.yaml` (project-specific workspace)
3. `~/.openjarvis/config/specialists.yaml` (global user workspace)

### Configuration Format (`specialists.yaml`)

```yaml
max_hops: 10 # Maximum specialist transitions per query

generalist:
  name: "generalist"
  system_prompt: |
    You are the ROUTER of OpenJarvis. Choose the best specialist:
    [ROUTE: math] - Calculations, statistics, proofs
    [ROUTE: code] - Programming, debugging, architecture
    [ROUTE: knowledge] - Factual questions and research
    [ROUTE: return] - Direct answer or tool result
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0

specialists:
  math:
    name: "math"
    system_prompt: "You are the MATH specialist. End replies with [RETURN]."
    base_url: "http://localhost:11434/v1" # Local Ollama
    model: "llama3"
    temperature: 0.0
    delegates_to: []

  code:
    name: "code"
    system_prompt: "You are the CODE specialist. End replies with [RETURN] or [DELEGATE: math]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]

  knowledge:
    name: "knowledge"
    system_prompt: "You are the KNOWLEDGE specialist. End replies with [RETURN]."
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.2
    delegates_to: []
```

---

## Built-In Tools Reference

OpenJarvis provides 29 built-in tools across 7 functional domains that models automatically invoke via standard function calling:

| Category | Tools | Descriptions |
| :--- | :--- | :--- |
| **Date & Time** | `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between` | Timestamps, timezone queries, date deltas, formatting |
| **Math** | `evaluate_expression`, `convert_units`, `solve_equation`, `prime_factorize` | Safe arithmetic evaluation, unit conversion, algebra, factorization |
| **File I/O** | `read_file`, `write_file`, `list_directory`, `search_in_files`, `file_info`, `delete_file` | File inspection, pattern search, metadata, and updates |
| **Web** | `fetch_url`, `search_web`, `fetch_wikipedia` | DuckDuckGo search, URL content extraction, Wikipedia lookups |
| **Code Execution** | `run_python`, `run_shell`, `lint_python` | Subprocess Python execution, shell commands, syntax linting |
| **Data Processing** | `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace` | JSON parsing, dot-notation extraction, CSV tables, regex |
| **Session Memory** | `store_note`, `recall_note`, `list_notes`, `delete_note` | Storing and retrieving context notes during a session |
| **Editor & SWE Execution** | `str_replace_editor`, `execute_bash` | Benchmark-standard string replacement and safe bash command execution |

---

## Keyboard Shortcuts & Commands

| Key / Command | Action |
| :--- | :--- |
| `Enter` | Submit current input |
| `Escape` then `Enter` | Insert a newline for multi-line input |
| `↑` / `↓` | Cycle through command history |
| `Ctrl+C` | Cancel current prompt or stop generation |
| `Ctrl+D` or `exit` | Exit OpenJarvis |

---

## Documentation

Full standalone user documentation is included in the [docs/](docs/) directory:
- [Installation Guide](docs/getting-started/installation.md)
- [Configuration Overview](docs/configuration/overview.md)
- [Provider Recipes](docs/configuration/providers.md)
- [Built-in Tools Manual](docs/tools/overview.md)
- [Troubleshooting & FAQ](docs/faq.md)

To view the offline documentation site:
```bash
uv sync --group docs
cd packages/openjarvis
uv run mkdocs serve
```
