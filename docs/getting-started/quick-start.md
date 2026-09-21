# Quick Start

Get OpenJarvis CLI running in under 2 minutes.

---

## 1. Installation

Download a pre-compiled standalone binary or run from source with `uv`:

=== "Standalone Binary"
    ```bash
    tar xzf openjarvis-v{{ version }}-linux-x86_64.tar.gz
    cd openjarvis-*
    chmod +x openjarvis
    ./openjarvis
    ```

=== "From Source (uv)"
    ```bash
    git clone https://github.com/bhanuponguru/openjarvis-cli.git
    cd openjarvis-cli
    uv sync
    uv run openjarvis
    ```

For system packages and alternative targets, see the [Installation Guide](installation.md).

---

## 2. Initial Setup Wizard

When launched without an existing configuration file, OpenJarvis initiates an interactive configuration setup:

```text
════════ OpenJarvis Multi-Agent Setup ════════

Welcome! No config.yaml configuration was found.
Let's create one so you can start using the OpenJarvis Multi-Agent System.

Step 1/3 — Choose your LLM provider
  ollama     — Local models via Ollama (free, private)
  openai     — OpenAI API (requires API key)
  anthropic  — Anthropic API (requires API key)
  google     — Google Gemini API (requires API key)
  custom     — Any OpenAI-compatible endpoint

Provider (ollama/openai/anthropic/google/custom): ollama
API base URL [http://localhost:11434/v1]: 
Model name [llama3]: 

Step 2/3 — Where to save the config
Save location [~/.openjarvis/config.yaml]: 

✓ Config written to ~/.openjarvis/config.yaml

oj> 
```

---

## 3. Provider Configuration

Configure your selected backend environment variables:

### Option A: Local Endpoints (Ollama / vLLM)
```bash
# Start local Ollama server and pull a model
ollama serve
ollama pull llama3.1
```

### Option B: Cloud Providers
```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google Gemini
export GEMINI_API_KEY="AIza..."
```

---

## 4. Canonical Workspace Configuration (`.openjarvis/config.yaml`)

To customize agent roles, models, and tool permissions for a project repository, define `.openjarvis/config.yaml`:

```yaml
version: "0.3.0"

default_provider: "openai"
default_model: "gpt-4o"

root_agent:
  name: "root"
  role: "coordinator"
  system_prompt: |
    You are the Root Coordinator. Coordinate multi-agent execution,
    spawn specialized worker agents via `spawn_agent`, and call `complete_task`
    when all objectives are satisfied.
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.1
  tools:
    - spawn_agent
    - connect_agents
    - report_findings
    - exit_agent
    - complete_task
    - read_file
    - search_dir

agents:
  researcher:
    role: "researcher"
    system_prompt: "You are the RESEARCHER agent. Report factual findings using `report_findings` and exit with `exit_agent`."
    model: "gpt-4o"
    temperature: 0.2
    tools:
      - fetch_url
      - search_web
      - read_file

  coder:
    role: "coder"
    system_prompt: "You are the CODER agent. Write, edit, and test software, then report results and exit with `exit_agent`."
    model: "gpt-4o"
    temperature: 0.1
    tools:
      - str_replace_editor
      - bash
      - run_python
      - run_pytest

tool_permissions:
  mode: "interactive"
  allowed_tools:
    - read_file
    - search_dir
    - search_in_files

limits:
  max_active_agents: 8
  max_spawn_depth: 3
  max_agent_turns: 15
```

---

## 5. Execution Example

```text
$ openjarvis

oj> Solve 15 squared plus 48 and check if the result is prime.

  [root] ⚙ spawn_agent {"role": "math", "task": "Evaluate 15**2 + 48 and factorize result"}
    → Agent 'agent-math' spawned
  [agent-math] ⚙ evaluate_expression {"expression": "15**2 + 48"}
    → 273
  [agent-math] ⚙ prime_factorize {"n": 273}
    → [3, 7, 13]
  [agent-math] ⚙ report_findings {"recipient": "root", "findings": "15^2 + 48 = 273. Factors: 3 * 7 * 13 (composite)."}
    → Findings delivered to 'root'
  [agent-math] ⚙ exit_agent {"status": "success"}
    → Agent 'agent-math' terminated
  [root] ⚙ complete_task {"summary": "Computed 273 and determined factors are 3, 7, 13"}

15 squared plus 48 is **273**. It is composite with prime factors 3, 7, and 13.
```

---

## CLI Shortcuts & Modes

- **Multi-line Input**: Press `Escape` followed by `Enter` (or `Alt+Enter`) to insert newlines.
- **Headless Non-Interactive**: Pass `-p` with `-y` for script integration:
  ```bash
  openjarvis -y -p "Run tests and summarize failures"
  ```
- **Exit Session**: Type `exit`, `quit`, or send `EOF` (`Ctrl+D`).

---

## Next Steps

- **[Configuration Overview →](../configuration/overview.md)** — Detailed config schema and limits.
- **[Multi-Agent System & Consensus →](../usage/routing.md)** — Actor engine mechanics and meta-tools.
- **[Built-in Tools Reference →](../tools/overview.md)** — Reference for all 49 tools.
- **[Security & Permissions →](../security.md)** — Permission modes and argument filtering.
