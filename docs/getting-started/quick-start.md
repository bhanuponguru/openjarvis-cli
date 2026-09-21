# Quick Start

Get OpenJarvis running in under 2 minutes.

---

## Step 1: Install OpenJarvis

Download a pre-built standalone binary or install via `uv`:

```bash
# Extract and run standalone binary (Linux / macOS)
tar xzf openjarvis-v{{ version }}-linux-x86_64.tar.gz
cd openjarvis-*
./openjarvis
```

For full installation options, see the [Installation Guide](installation.md).

---

## Step 2: First Launch & Interactive Wizard

When launched without a configuration file, OpenJarvis automatically starts an **interactive setup wizard**:

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

Once complete, OpenJarvis enters the interactive chat session immediately!

---

## Step 3: Choose Your AI Provider

OpenJarvis works with any OpenAI-compatible API. You can configure:

### Option A: Ollama (Local, Free, Private)
- **Best for**: Total privacy, offline execution, no API bills
- Start Ollama and pull your models:
  ```bash
  ollama serve
  ollama pull llama3
  ```

### Option B: OpenAI (Cloud)
- **Best for**: Maximum performance and model capability
- Export your API key in your shell:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

### Option C: Anthropic / Google Gemini / Custom
- Export your respective key:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  export GOOGLE_API_KEY="AIza..."
  ```

---

## Step 4: Example Configuration (`.openjarvis/config.yaml`)

If you want to manually create or customize your configuration, create `.openjarvis/config.yaml`:

```yaml
root_agent:
  name: "root"
  role: "coordinator"
  system_prompt: |
    You are the Root Agent of OpenJarvis. Coordinate multi-agent tasks,
    spawn specialized child agents with `spawn_agent`, and call `complete_task`
    when work is done.
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.1

agents:
  researcher:
    name: "researcher"
    role: "researcher"
    system_prompt: "You are the RESEARCHER agent. Report findings with `report_findings` and exit with `exit_agent`."
    provider: "openai"
    model: "gpt-4o"
    tools: ["fetch_webpage", "search_web"]

  coder:
    name: "coder"
    role: "coder"
    system_prompt: "You are the CODER agent. Write and verify code, then exit with `exit_agent`."
    provider: "openai"
    model: "gpt-4o"
    tools: ["str_replace_editor", "bash", "execute_python"]

limits:
  max_active_agents: 8
  max_spawn_depth: 3
  max_agent_turns: 15
```

---

## Step 5: Interactive Chatting

Start OpenJarvis and ask questions naturally:

```text
$ openjarvis

oj> What is 15 squared plus 48?

  ↳ routing: generalist → math
  ⚙ tool: evaluate_expression {"expression": "15**2 + 48"}
    → 273

15 squared (225) plus 48 is **273**.

oj> Search for the latest release of Python

  ↳ routing: generalist → knowledge
  ⚙ tool: search_web {"query": "latest Python release"}
    → [{"title": "Python 3.13 Release Notes", ...}]

The latest stable release of Python is Python 3.13...

oj> exit
```

---

## Tips & Shortcuts

- **Multi-line input**: Press `Escape` followed by `Enter` to insert a newline.
- **Command history**: Use the `↑` and `↓` arrow keys to navigate previous prompts.
- **Custom config path**: Set `OJ_CONFIG=/path/to/my-config.yaml openjarvis`.
- **Exit session**: Type `exit`, `quit`, or press `Ctrl+C` / `Ctrl+D`.

---

## Next Steps

- **[Configuration Overview →](../configuration/overview.md)** — Detailed configuration options
- **[Built-in Tools Reference →](../tools/overview.md)** — Explore all 49 tools
- **[Troubleshooting →](../troubleshooting.md)** — Common questions and solutions

