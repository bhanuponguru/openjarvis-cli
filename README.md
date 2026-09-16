# OpenJarvis CLI (`openjarvis-cli`)

> **Autonomous multi-model agentic CLI & orchestrator routing tasks across specialized LLMs**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI version](https://badge.fury.io/py/openjarvis-cli.svg)](https://pypi.org/project/openjarvis-cli/)

OpenJarvis CLI is an intelligent terminal client that coordinates a team of specialized language models across any model provider. Instead of forcing one model to do everything, OpenJarvis dynamically routes tasks to specialized agents (coding, mathematics, factual knowledge, and planning) and executes built-in tools when needed.

---

## Key Features

- 🎯 **Multi-Model Orchestration**: Dynamic LangGraph state machine routing requests across specialized agents.
- 🔌 **Provider Agnostic**: Mix and match Ollama (free local models), OpenAI, Groq, Anthropic, Gemini, or any OpenAI-compatible API in one session.
- 🛠️ **29 Production-Ready Built-In Tools**: Terminal execution (`execute_bash`), file editing (`str_replace_editor`), web search, math solvers, datetime utilities, and session memory.
- 🛡️ **Interactive Security Sandbox**: Granular permission manager intercepting tool calls with interactive user approvals and path constraints.
- 💻 **Modern Terminal Interface**: Interactive REPL with syntax-highlighted Markdown rendering, multiline input, and live routing events.
- 🚀 **Zero-Dependency Standalone Binaries**: Precompiled executables available for Linux, macOS, and Windows.

---

## Quick Start

### 1. Installation

#### Via `uv` (Recommended)
```bash
uv tool install openjarvis-cli
```

#### Via `pip`
```bash
pip install openjarvis-cli
```

#### Standalone Binary (Zero Python Required)
Download the latest executable for your platform from [GitHub Releases](https://github.com/bhanuponguru/openjarvis-cli/releases).

#### From Source
```bash
git clone https://github.com/bhanuponguru/openjarvis-cli.git
cd openjarvis-cli
uv sync
```

---

### 2. Launching OpenJarvis

Launch the terminal client:
```bash
openjarvis
# or use the short alias:
oj
```

On first launch, if no configuration is found, an interactive setup wizard will guide you to configure your preferred provider (Ollama, OpenAI, Anthropic, etc.).

---

### 3. Command-Line Options

```text
Usage: openjarvis [OPTIONS] [QUERY]

Options:
  -c, --config PATH     Path to specialists.yaml configuration file
  --model TEXT          Override generalist model name
  --provider TEXT       Override default provider (e.g. ollama, openai, anthropic)
  --version             Show version and exit
  --help                Show this message and exit
```

To run non-interactively with a single prompt:
```bash
oj "Calculate 15% of 850 and write a python script to verify"
```

---

## Configuration (`specialists.yaml`)

OpenJarvis uses a simple YAML file defining your team of specialists:

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

  math:
    provider: "openai"
    model: "gpt-4o-mini"
    temperature: 0.0
```

---

## Documentation

Full documentation is available at [https://bhanuponguru.tech/openjarvis-cli](https://bhanuponguru.tech/openjarvis-cli):
- [Installation Guide](docs/getting-started/installation.md)
- [Configuration Reference](docs/configuration/overview.md)
- [Built-In Tools Catalog](docs/tools/overview.md)
- [Security & Sandboxing](docs/security.md)
- [Developer & Contributing Guide](docs/developer-guide.md)

---

## License

Apache 2.0 License.
