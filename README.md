# OpenJarvis CLI (`openjarvis-cli`)

> **Autonomous multi-model agentic CLI & orchestrator routing tasks across specialized LLMs**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/openjarvis-cli.svg)](https://pypi.org/project/openjarvis-cli/)
[![Documentation](https://img.shields.io/badge/docs-mkdocs--material-blue.svg)](https://bhanuponguru.tech/openjarvis-cli)

OpenJarvis CLI is an intelligent terminal client that coordinates a team of specialized language models across any model provider. Instead of forcing one generalist model to do everything, OpenJarvis dynamically routes tasks to specialized agents (coding, mathematics, web research, data processing, and planning) and executes built-in tools with real-time feedback.

---

## Key Features

- 🎯 **Multi-Model Orchestration**: Dynamic LangGraph state machine routing requests across specialized agents.
- 🔌 **Provider Agnostic**: Mix and match Ollama (free & private local models), OpenAI, Anthropic, Gemini, Groq, or any OpenAI-compatible API in one session.
- 🛠️ **49 Production-Ready Built-In Tools**: Comprehensive tools spanning 9 functional domains (file inspection, Git & patch management, web lookups, REST requests, code execution, AST math solvers, SQLite queries, datetime operations, and persistent memory).
- 🛡️ **Interactive Security Sandbox**: Granular permission manager intercepting tool calls with interactive user approvals and directory constraints.
- 💻 **Modern Terminal Interface**: Interactive REPL with syntax-highlighted Markdown rendering, multiline input, live routing events, and history search.
- 📦 **Instant Execution & Packaging**: Run immediately with `uvx`, install via `uv tool` or `pip`, or run compiled standalone binaries.
- 🏷️ **Single-Source Versioning**: Integrated semantic versioning with automatic package, CLI, and documentation synchronization.

---

## Quick Start

### 1. Installation

#### Instant Run (No Installation Needed)
```bash
uvx openjarvis-cli
```

#### Via `uv` (Recommended Tool Install)
```bash
uv tool install openjarvis-cli
```

#### Via `pip`
```bash
pip install openjarvis-cli
```

#### Standalone Binary (Zero Python Required)
Download precompiled self-contained executables for Linux, macOS, or Windows from [GitHub Releases](https://github.com/bhanuponguru/openjarvis-cli/releases).

#### From Source
```bash
git clone https://github.com/bhanuponguru/openjarvis-cli.git
cd openjarvis-cli
uv sync
uv run openjarvis
```

---

### 2. Launching OpenJarvis

Launch the interactive terminal client:
```bash
openjarvis
# or use the short alias:
oj
```

On first launch, if no configuration is found, an interactive setup wizard will guide you to configure your preferred provider (Ollama, OpenAI, Anthropic, Gemini, etc.).

---

### 3. Command-Line Options

```text
Usage: openjarvis [-h] [-c CONFIG] [--model MODEL] [--provider PROVIDER]
                  [--update-tools] [-V] [query ...]

Options:
  -c, --config CONFIG  Path to specialists.yaml configuration file
  --model MODEL        Override generalist model name
  --provider PROVIDER  Override default provider (e.g. ollama, openai, anthropic)
  --update-tools       Re-index and update tool embedding vectors
  -V, --version        Show version and exit
  -h, --help           Show this message and exit
```

#### Non-Interactive Single-Prompt Mode
Run a one-off prompt directly without entering the REPL:
```bash
oj "Calculate compound interest on $10,000 at 5% for 10 years and write a python script to verify"
```

#### Override Models on the Fly
```bash
oj --provider anthropic --model claude-3-5-sonnet-20241022
```

---

### 4. Interactive REPL Commands

Inside the interactive terminal session (`oj>`), the following commands are available:

| Command | Description |
| :--- | :--- |
| `/help` | Show available commands and keyboard shortcuts |
| `/version`, `/v` | Show the active `openjarvis-cli` version |
| `/clear` | Clear the terminal screen |
| `/update-tools` | Re-index tool embedding vectors |
| `/exit`, `/quit` | Exit the OpenJarvis session |
| `↑` / `↓` | Browse prompt history |
| `Ctrl-R` | Reverse search input history |
| `Esc` + `Enter` | Multi-line input mode |

---

## Built-In Tools (49 Tools Across 9 Modules)

OpenJarvis includes 49 native tools automatically invoked by models via function calling:

| Module | Count | Key Tools |
| :--- | :--- | :--- |
| **[File I/O](docs/tools/files.md)** | 9 | `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file` |
| **[Git & Version Control](docs/tools/git.md)** | 4 | `git_diff`, `git_status`, `git_log`, `apply_patch` |
| **[Web & API](docs/tools/web.md)** | 5 | `search_web`, `fetch_url`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec` |
| **[Code Execution](docs/tools/code.md)** | 4 | `run_python`, `run_shell`, `lint_python`, `run_pytest` |
| **[Code Editor & Terminal](docs/tools/editor.md)** | 3 | `str_replace_editor`, `execute_bash`, `bash` |
| **[Data Processing](docs/tools/data.md)** | 6 | `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query` |
| **[Math & Arithmetic](docs/tools/math.md)** | 4 | `evaluate_expression`, `convert_units`, `solve_equation`, `prime_factorize` |
| **[Date & Time](docs/tools/datetime.md)** | 4 | `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between` |
| **[Session & Memory](docs/tools/memory.md)** | 10 | `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and note storage aliases |

---

## Configuration (`specialists.yaml`)

OpenJarvis uses a clean YAML configuration defining your generalist router and specialized agents:

```yaml
generalist:
  provider: "ollama"
  model: "llama3.2"
  temperature: 0.0

specialists:
  code:
    provider: "ollama"
    model: "qwen2.5-coder:7b"
    temperature: 0.0
    system_prompt: "You are an expert programming specialist..."

  math:
    provider: "openai"
    model: "gpt-4o-mini"
    temperature: 0.0
    system_prompt: "You are a mathematical calculation and reasoning specialist..."

  knowledge:
    provider: "anthropic"
    model: "claude-3-5-haiku-20241022"
    temperature: 0.2
    system_prompt: "You are a research and factual knowledge specialist..."
```

---

## Versioning & Releases

OpenJarvis CLI uses **Semantic Versioning (SemVer)** with a single source of truth in `src/openjarvis/_version.py`, integrated with Hatchling dynamic versioning:

```bash
# Bump patch release (e.g. 0.2.0 -> 0.2.1)
python scripts/bump-version.py patch

# Bump minor release (e.g. 0.2.0 -> 0.3.0)
python scripts/bump-version.py minor

# Bump major release (e.g. 0.2.0 -> 1.0.0)
python scripts/bump-version.py major
```

Build and publish:
```bash
uv build
uv publish
```

---

## Documentation

Comprehensive documentation is available at [https://bhanuponguru.tech/openjarvis-cli](https://bhanuponguru.tech/openjarvis-cli):
- [Installation Guide](docs/getting-started/installation.md)
- [Quick Start Guide](docs/getting-started/quick-start.md)
- [Configuration Reference](docs/configuration/overview.md)
- [Built-In Tools Catalog (49 Tools)](docs/tools/overview.md)
- [Security & Sandboxing](docs/security.md)
- [Developer & Contributing Guide](docs/developer-guide.md)

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
