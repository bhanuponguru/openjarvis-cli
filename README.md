# OpenJarvis — Intelligent Multi-Model AI Orchestrator

OpenJarvis is a sophisticated AI assistant that orchestrates conversations across multiple specialized language models. Instead of relying on a single model for all tasks, OpenJarvis intelligently routes your requests through a team of specialist models — each fine-tuned for specific domains like mathematics, code generation, knowledge retrieval, and creative writing.

---

## 📖 Documentation

This package includes complete standalone user documentation:

- **Binary releases:** Includes `docs/` folder with full HTML documentation
- **Source:** See [docs/](docs/) directory — run `cd docs && mkdocs serve` to view locally
- **Quick start:** [docs/getting-started/quick-start.md](docs/getting-started/quick-start.md)

The documentation covers installation, configuration, all 29 built-in tools, troubleshooting, and usage examples.

## Why OpenJarvis?

**🎯 Specialized Intelligence**
Different AI models excel at different tasks. OpenJarvis lets you leverage the best model for each part of your conversation, combining their strengths seamlessly.

**🔌 Provider Agnostic**
Works with any OpenAI-compatible API: Ollama (local and free), OpenAI, Anthropic Claude, Groq, OpenRouter, or your own custom inference server.

**🛠️ Production-Ready Tools**
Ships with 29 built-in tools for web search, code execution, file operations, mathematical calculations, and more — no additional configuration required.

**🔍 Transparent Routing**
See exactly which specialists contributed to your answer, giving you full visibility into the decision-making process.

**🎨 Flexible Configuration**
Mix and match providers, models, and temperatures per specialist. Use GPT-4 for orchestration, local Llama for math, and Groq for fast knowledge retrieval — all in one conversation.

---

## Quick Start

### Installation

**From Binary (No Python Required):**

Download the standalone binary for your platform from [Releases](https://github.com/yourorg/openjarvis/releases):

```bash
# Linux / macOS
tar xzf openjarvis-*.tar.gz
chmod +x openjarvis
./openjarvis

# Windows
# Extract ZIP and run openjarvis.exe
```

**From Source:**

```bash
# Requires Python ≥ 3.13 and uv
git clone https://github.com/yourorg/openjarvis.git
cd OpenJarvis
uv sync --all-packages
uv run openjarvis
```

### Basic Configuration

Create `specialists.yaml`:

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Route requests using:
    [ROUTE: return] - Final answer
    [ROUTE: math] - Math questions
    [ROUTE: code] - Code tasks
    [ROUTE: knowledge] - Facts and research
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"

specialists:
  math:
    system_prompt: "Math specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"  # Ollama
    model: "llama3"
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    system_prompt: "Code specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  knowledge:
    system_prompt: "Knowledge specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.5
    delegates_to: ["tool_use"]

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

Set your API key and run:

```bash
export OPENAI_API_KEY="sk-..."
openjarvis
```

---

## Features

### Multi-Model Routing

OpenJarvis intelligently routes conversations through specialist models:

```
You: "Calculate 15% of 80 and explain when this is useful"

  routing: generalist → math → tool_use → math → generalist

Answer: 12.0. This calculation is commonly used for computing tips,
discounts, tax amounts, and understanding proportional relationships.
```

Complex queries automatically chain through multiple specialists without manual intervention.

### 29 Built-In Tools

Specialists with tool access can automatically invoke:

**Web & Network:**
- `web_search` — DuckDuckGo search
- `fetch_url` — Retrieve webpage content
- `http_get`, `http_post` — HTTP requests

**Mathematics:**
- `calculate` — Evaluate expressions
- `solve_equation` — Solve algebraic equations
- `convert_units` — Unit conversions

**Date & Time:**
- `get_current_time`, `get_current_date`
- `days_between`, `add_days`, `format_date`

**Code Execution:**
- `run_python` — Execute Python code
- `run_shell` — Execute shell commands

**File System:**
- `read_file`, `write_file`
- `list_directory`, `file_exists`, `get_file_info`

**Text Processing:**
- `count_words`, `extract_json`, `format_json`
- `truncate_text`, `replace_text`

**System:**
- `get_env_var`, `get_system_info`

**Memory:**
- `save_note`, `get_note`, `list_notes`

**Cryptography:**
- `hash_text` — Generate cryptographic hashes

Tools are invoked automatically when needed — no explicit commands required.

### Provider Flexibility

Mix providers to optimize cost, speed, and capabilities:

```yaml
generalist:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"  # Fast orchestration

specialists:
  math:
    base_url: "http://localhost:11434/v1"
    model: "llama3"  # Local, free

  knowledge:
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"  # Fast, affordable
    api_key_env: "GROQ_API_KEY"
```

### Rich Terminal Output

- **Routing indicators:** See which specialists are working
- **Formatted answers:** Markdown rendering for beautiful output
- **Tool execution feedback:** Know when tools are running
- **Error handling:** Clear error messages with suggestions

---

## Architecture

OpenJarvis uses a **conductor pattern** to orchestrate multi-model conversations:

```
User Query
    ↓
┌─────────────────────────┐
│   Generalist (Conductor) │ — Decides routing
└─────────────────────────┘
    ↓          ↓         ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Math   │ │  Code   │ │Knowledge│ — Specialists
└─────────┘ └─────────┘ └─────────┘
    ↓          ↓         ↓
┌─────────────────────────┐
│       Tool Execution     │ — Built-in tools
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Generalist Synthesis   │ — Final answer
└─────────────────────────┘
```

### Routing Protocol

Models communicate using simple text tags:

**Generalist (Orchestrator):**
- `[ROUTE: return]` — Send as final answer
- `[ROUTE: math]` — Route to math specialist
- `[ROUTE: code]` — Route to code specialist
- `[ROUTE: knowledge]` — Route to knowledge specialist

**Specialists:**
- `[RETURN]` — Send back to generalist
- `[DELEGATE: specialist]` — Delegate to another specialist

Tags are automatically removed from the final output.

### Safety Features

- **Loop Prevention:** `max_hops` setting prevents infinite routing loops
- **Delegation Validation:** Specialists can only delegate to approved targets
- **Timeout Protection:** Per-call timeouts prevent hanging requests
- **Graceful Degradation:** On errors, return partial results instead of failing completely

---

## Configuration

### Configuration File Locations

OpenJarvis searches for configuration in this order:

1. `OJ_CONFIG` environment variable (highest priority)
2. `./specialists.yaml` (current directory)
3. `~/.config/openjarvis/specialists.yaml` (user config)
4. `/etc/openjarvis/specialists.yaml` (system-wide, Linux/macOS)

Override:
```bash
OJ_CONFIG=/path/to/config.yaml openjarvis
```

### Configuration Options

**Global Settings:**

```yaml
max_hops: 10  # Maximum routing steps per query
```

**Per-Specialist Settings:**

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `system_prompt` | ✅ Yes | — | Role and routing instructions |
| `base_url` | No | `http://localhost:11434/v1` | API endpoint |
| `model` | No | `llama3` | Model name |
| `api_key_env` | No | — | Environment variable with API key |
| `temperature` | No | `0.7` | Sampling temperature (0.0-1.0) |
| `max_tokens` | No | — | Response length limit |
| `timeout` | No | `60.0` | Request timeout (seconds) |
| `delegates_to` | No | `[]` | Specialists this one can delegate to |

---

## Use Cases

### Personal AI Assistant

```
> What's on my calendar today?
  routing: generalist → tool_use → generalist

You have 3 meetings today: standup at 9 AM, design review at 2 PM,
and team sync at 4 PM.
```

### Development Helper

```
> Write a Python function to validate email addresses
  routing: generalist → code → generalist

import re

def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

### Research Assistant

```
> What are the latest developments in quantum computing?
  routing: generalist → knowledge → tool_use → knowledge → generalist

[Answer includes recent research gathered from web search]
```

### Multi-Step Problem Solving

```
> Calculate Japan's GDP, convert to euros, then find the square root
  routing: generalist → knowledge → tool_use → knowledge
  routing: knowledge → math → tool_use → math
  routing: math → generalist

Japan's GDP is ~$4.2 trillion. Converting to euros at current rates:
~€3.8 trillion. Square root: ~€1.95 million.
```

---

## Python API

While OpenJarvis is primarily a CLI tool, it can also be used programmatically:

```python
from openjarvis import Conductor

# Initialize with config file
conductor = Conductor(config_path="specialists.yaml")

# Send a message (returns generator)
events = conductor.chat("What's 15% of 80?")

# Process events
for event in events:
    if event["type"] == "route":
        print(f"Routing: {event['from_role']} → {event['to_role']}")
    elif event["type"] == "final":
        print(f"Answer: {event['content']}")

# Save conversation history
conductor.save_history("session.json")

# Load conversation history
conductor.load_history("session.json")
```

---

## Dependencies

OpenJarvis has minimal dependencies:

- **openai** ≥ 1.0.0 — OpenAI Python SDK (works with all compatible APIs)
- **pyyaml** ≥ 6.0 — YAML configuration parsing
- **rich** ≥ 13.0 — Terminal formatting and Markdown rendering
- **ddgs** ≥ 9.0 — DuckDuckGo search for `web_search` tool
- **pytz** ≥ 2024.1 — Timezone support for date/time tools

**Notably absent:**
- ❌ No `torch` — OpenJarvis is a client, not an inference engine
- ❌ No `jarvis` package — Clean separation between client and brain
- ❌ No heavyweight ML frameworks

This keeps the client lightweight and portable.

---

## Performance

### Typical Latency

- **Simple queries:** < 2 seconds (single-hop)
- **Complex queries:** 3-10 seconds (multi-hop with tools)
- **Streaming:** First tokens appear in < 1 second

Latency depends on:
- Provider API speed
- Model size and complexity
- Number of routing hops
- Tool execution time

### Optimization Tips

**Fast Configuration:**
```yaml
generalist:
  model: "gpt-4o-mini"  # Fast, cheap
  temperature: 0.7
  timeout: 30.0
  max_tokens: 500

specialists:
  math:
    base_url: "https://api.groq.com/openai/v1"  # Groq is very fast
    model: "llama-3.1-8b-instant"
    temperature: 0.3
```

**Cost-Optimized Configuration:**
```yaml
generalist:
  base_url: "http://localhost:11434/v1"  # Local Ollama = free
  model: "llama3"
```

---

## Troubleshooting

### Configuration File Not Found

```
Error: specialists.yaml not found
```

**Solutions:**
1. Create `specialists.yaml` in current directory
2. Set `OJ_CONFIG`: `OJ_CONFIG=/path/to/config.yaml openjarvis`
3. Place config in `~/.config/openjarvis/specialists.yaml`

### API Key Not Set

```
Error: OPENAI_API_KEY environment variable not set
```

**Solution:**
```bash
export OPENAI_API_KEY="your-key-here"
```

Make permanent: Add to `~/.bashrc` or `~/.zshrc`

### Connection Refused

```
Error calling generalist: Connection refused
```

**For Ollama:**
```bash
# Start Ollama
ollama serve

# Pull model
ollama pull llama3
```

**For jarvis server:**
```bash
uv run jarvis-serve --dev
```

### Empty Responses

**Check:**
1. Model name is correct: `ollama list`
2. API key is valid
3. Base URL is correct
4. Network connection works

---

## Security & Privacy

**Local Operation:** Use Ollama for fully local, private AI assistance — no data leaves your machine.

**API Key Safety:** API keys are read from environment variables, never stored in configuration files.

**Network Security:** When using local models (Ollama, jarvis), no network requests are made.

**Audit Trail:** Routing indicators show exactly which models processed your data.

---

## What's Next

- **Full Documentation:** See [OpenJarvis User Guide](../../docs/user/openjarvis/index.md)
- **jarvis Local Server:** Run your own inference engine — [jarvis Guide](../../docs/user/jarvis/index.md)
- **Developer Docs:** Understand the internals — [Developer Guide](../../docs/DEVELOPER_GUIDE.md)
- **Contributing:** [Contribution Guidelines](../../docs/DEVELOPER_GUIDE.md)

---

## License

[Your License Here]

---

## Links

- **Documentation:** [Full Docs](../../docs/)
- **Issues:** [GitHub Issues](https://github.com/yourorg/openjarvis/issues)
- **Releases:** [GitHub Releases](https://github.com/yourorg/openjarvis/releases)
- **Source Code:** [GitHub Repository](https://github.com/yourorg/openjarvis)
