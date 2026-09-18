# Quick Start

Get OpenJarvis running in under 2 minutes.

---

## Step 1: Install OpenJarvis

Download a pre-built standalone binary or install via `uv`:

```bash
# Extract and run standalone binary (Linux / macOS)
tar xzf openjarvis-*.tar.gz
cd openjarvis-*
./openjarvis
```

For full installation options, see the [Installation Guide](installation.md).

---

## Step 2: First Launch & Interactive Wizard

When launched without a configuration file, OpenJarvis automatically starts an **interactive setup wizard**:

```text
════════ OpenJarvis Setup ════════

Welcome! No specialists.yaml config was found.
Let's create one so you can start using OpenJarvis.

Step 1/3 — Choose your LLM provider
  ollama  — Local models via Ollama (free, private)
  openai  — OpenAI API (requires API key)
  custom  — Any OpenAI-compatible endpoint

Provider (ollama/openai/custom): ollama
API base URL [http://localhost:11434/v1]: 
Model name [llama3]: 

Step 2/3 — Where to save the config
Save location [~/.config/openjarvis/specialists.yaml]: 

✓ Config written to ~/.config/openjarvis/specialists.yaml

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

### Option C: Groq / OpenRouter / Custom
- Export your respective key:
  ```bash
  export GROQ_API_KEY="gsk_..."
  ```

---

## Step 4: Example Configuration (`specialists.yaml`)

If you want to manually create or customize your configuration, create `specialists.yaml`:

```yaml
max_hops: 10

generalist:
  name: "generalist"
  system_prompt: |
    You are OpenJarvis. Route requests using:
    [ROUTE: math] - Math calculations, proofs, and algebra
    [ROUTE: code] - Programming and debugging
    [ROUTE: knowledge] - Factual questions and research
    [ROUTE: return] - Final answer or tool results
  provider: "openai"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0

specialists:
  math:
    name: "math"
    system_prompt: "You are the MATH specialist. Solve calculations step-by-step. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: []

  code:
    name: "code"
    system_prompt: "You are the CODE specialist. Write clean code. End with [RETURN] or [DELEGATE: math]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.0
    delegates_to: ["math"]

  knowledge:
    name: "knowledge"
    system_prompt: "You are the KNOWLEDGE specialist. Answer factual questions. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: []
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

