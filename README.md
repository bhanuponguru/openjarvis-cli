# OpenJarvis CLI (`openjarvis-cli`)

> Asynchronous, vendor-agnostic multi-agent orchestration CLI and terminal client coordinating task execution across dynamic agent graphs.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs--material-blue.svg)](https://openjarvis-cli.bhanuponguru.tech)

OpenJarvis is an agentic orchestration CLI and terminal client. It coordinates task execution across a dynamic Multi-Agent System (MAS) of autonomous Conductor agent nodes using an asynchronous actor engine, neighbor-based messaging, and a strict bottom-up exit hierarchy.

---

## Architecture Overview

- **Dynamic Multi-Agent System (MAS)**: Asynchronous actor engine where the Root Coordinator decomposes complex objectives, spawns specialized child agents (`spawn_agent`), establishes communication edges (`connect_agents`), and supervises completion.
- **Strict Bottom-Up Exit Hierarchy**: Child agents must finish their assignments and emit deliverables (`exit_agent`) before parent agents can exit. The Root Agent concludes the task with `complete_task` only after all subordinates have exited.
- **Shared Artifact Store**: Structured deliverables (code patches, markdown reports, data models) are persisted with content-addressable SHA-256 identifiers in memory and under `.openjarvis/artifacts/`.
- **Peer-to-Peer Neighbor Consensus**: Connected agents exchange milestones and evidence via `report_findings`, incorporating updates directly into their ongoing execution turns.
- **Provider Agnostic**: Direct integration with Ollama (local inference), OpenAI, Anthropic, Google Gemini, Groq, or any OpenAI-compatible HTTP endpoint.
- **49 Built-in Tools**: 9 functional modules covering file operations, atomic string editing, Git version control, web search, sandboxed execution, AST math solvers, SQLite, datetime arithmetic, and persistent memory.
- **Tool Permissions & Guardrails**: Granular permission manager intercepting tool calls with interactive, autonomous, and allowlist modes, argument pattern matching, and safety classification.
- **Pure Python Architecture**: Target: Python 3.13+ / 3.14 with zero CUDA or PyTorch dependencies.

---

## Installation

### Option 1: Standalone Binary
Download precompiled standalone binaries for Linux, macOS, or Windows from [GitHub Releases](https://github.com/bhanuponguru/openjarvis-cli/releases). No Python runtime is required.

```bash
tar xzf openjarvis-*.tar.gz
cd openjarvis-*
chmod +x openjarvis
./openjarvis
```

### Option 2: From Source with `uv`
```bash
git clone https://github.com/bhanuponguru/openjarvis-cli.git
cd openjarvis-cli
uv sync --group dev --group docs --group build
uv run openjarvis
```

---

## Command-Line Usage

```text
usage: openjarvis [-h] [-c CONFIG] [-v] [--model MODEL] [--provider PROVIDER]
                  [--update-tools] [-y]
                  [--mode {interactive,autonomous,allowlist}] [-V]
                  [query ...]

Autonomous dynamic Multi-Agent System (MAS) coordinating specialized Conductor
agents

positional arguments:
  query                 Optional non-interactive query to execute

options:
  -h, --help            Show this help message and exit
  -c, --config CONFIG   Path to config.yaml configuration file
  -v, --verbose         Display live inter-agent messaging, spawning, and tool events
  --model MODEL         Override root agent model name
  --provider PROVIDER   Override default provider (e.g. ollama, openai, anthropic)
  --update-tools        Re-index and update tool embedding vectors
  -y, --auto-approve    Automatically approve tool executions without prompting
  --mode {interactive,autonomous,allowlist}
                        Tool permission enforcement mode (default: interactive)
  -V, --version         Show program's version number and exit
```

### Execution Modes

#### Interactive REPL
Launch the terminal interface:
```bash
openjarvis
# or short alias:
oj
```

On first run without a configuration, OpenJarvis launches an interactive setup wizard to configure your preferred provider and output path.

#### Non-Interactive Execution
Execute a prompt directly from the shell:
```bash
oj "Calculate 987 multiplied by 654 and return the result"
```

#### Autonomous Execution (`-y` / `--auto-approve`)
Run multi-step tasks without interactive confirmation prompts:
```bash
oj -y "Inspect the repository, identify missing docstrings, and generate a report"
```

#### Verbose Multi-Agent Trace (`-v`)
Display real-time agent spawning, neighbor messaging, and tool calls:
```bash
oj -v -y "Decompose this task: spawn a researcher to check API docs, and a coder to write tests"
```

---

## REPL Commands & Shortcuts

| Command | Description |
| :--- | :--- |
| `/help` | Display available commands and keyboard shortcuts |
| `/version` | Print active `openjarvis-cli` version |
| `/clear` | Clear terminal screen |
| `/update-tools` | Re-index and cache tool embedding vectors |
| `/exit`, `/quit` | Terminate session |
| `↑` / `↓` | Navigate input history |
| `Ctrl-R` | Incremental history search |
| `Esc` + `Enter` | Insert newline in multiline input mode |

---

## Built-In Tool Modules

| Module | Count | Capabilities |
| :--- | :---: | :--- |
| **[File Operations](docs/tools/files.md)** | 9 | `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file` |
| **[Git & Version Control](docs/tools/git.md)** | 4 | `git_diff`, `git_status`, `git_log`, `apply_patch` |
| **[Web & API](docs/tools/web.md)** | 5 | `search_web`, `fetch_url`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec` |
| **[Code Execution](docs/tools/code.md)** | 4 | `run_python`, `run_shell`, `lint_python`, `run_pytest` |
| **[Code Editor & Terminal](docs/tools/editor.md)** | 3 | `str_replace_editor`, `execute_bash`, `bash` |
| **[Data Processing](docs/tools/data.md)** | 6 | `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query` |
| **[Math & Arithmetic](docs/tools/math.md)** | 4 | `evaluate_expression`, `convert_units`, `solve_equation`, `prime_factorize` |
| **[Date & Time](docs/tools/datetime.md)** | 4 | `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between` |
| **[Session Memory](docs/tools/memory.md)** | 10 | `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and note storage aliases |

---

## Configuration (`.openjarvis/config.yaml`)

```yaml
root_agent:
  name: "root"
  role: "coordinator"
  system_prompt: |
    You are the Root Agent of OpenJarvis. Coordinate multi-agent tasks,
    spawn specialized child agents with `spawn_agent`, and call `complete_task`
    when work is completed.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.1
  max_hops: 15

agents:
  researcher:
    name: "researcher"
    role: "researcher"
    system_prompt: "You are the RESEARCHER agent. Report findings with `report_findings` and exit with `exit_agent`."
    provider: "openai"
    model: "gpt-4o"
    tools: ["fetch_url", "search_web", "fetch_wikipedia"]

  coder:
    name: "coder"
    role: "coder"
    system_prompt: "You are the CODER agent. Write, debug, and verify code, then exit with `exit_agent`."
    provider: "openai"
    model: "gpt-4o"
    tools:
      - "str_replace_editor"
      - "bash"
      - "run_python"
      - "lint_python"
      - "run_pytest"
      - "git_status"
      - "git_diff"

tool_permissions:
  mode: "interactive"

limits:
  max_active_agents: 8
  max_spawn_depth: 3
  max_agent_turns: 15
  turn_timeout_seconds: 300.0
```

---

## Versioning & Releases

OpenJarvis CLI uses dynamic Git-tag semantic versioning via `hatch-vcs`:

- **Tagged Releases**: Annotated Git tags (`vX.Y.Z`) determine package, CLI, and documentation versions.
- **Development Builds**: Commits ahead of a release tag produce PEP 440 development versions (e.g. `0.3.1.dev3`).

```bash
# Tag release using bumper script:
python scripts/bump-version.py patch   # e.g. v0.3.0 -> v0.3.1
python scripts/bump-version.py minor   # e.g. v0.3.0 -> v0.4.0
python scripts/bump-version.py major   # e.g. v0.3.0 -> v1.0.0

# Build release wheels and sdist:
uv build
```

---

## Documentation

Full documentation is available at [openjarvis-cli.bhanuponguru.tech](https://openjarvis-cli.bhanuponguru.tech):
- [Installation Guide](docs/getting-started/installation.md)
- [Quick Start Guide](docs/getting-started/quick-start.md)
- [Configuration Reference](docs/configuration/overview.md)
- [Agents & Profiles](docs/configuration/agents.md)
- [Multi-Agent Routing & Consensus](docs/usage/routing.md)
- [Built-In Tools Reference](docs/tools/overview.md)
- [Security & Sandboxing](docs/security.md)
- [Developer Guide](docs/developer-guide.md)

---

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
