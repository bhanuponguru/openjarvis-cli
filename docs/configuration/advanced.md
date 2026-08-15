# Advanced Configuration

This page covers power-user configuration options for OpenJarvis.

---

## Configuration File Locations

OpenJarvis searches for configuration in this order (first match wins):

1. `--config` flag: `openjarvis --config /path/to/config.yaml`
2. `OJ_CONFIG` environment variable
3. `specialists.yaml` in the current working directory
4. `~/.config/openjarvis/specialists.yaml`

### Per-Project Configs

Keep a `specialists.yaml` in each project directory and run OpenJarvis from there:

```
my-project/
├── specialists.yaml    ← OpenJarvis uses this when run from here
├── src/
└── ...
```

### Global Config

For a config that works everywhere:

```bash
mkdir -p ~/.config/openjarvis
cp specialists.yaml ~/.config/openjarvis/specialists.yaml
```

### Switching Configs

```bash
# Use a specific config
openjarvis --config ~/configs/coding.yaml

# Use an environment variable
export OJ_CONFIG=~/configs/research.yaml
openjarvis
```

---

## Environment Variable Substitution

API keys are loaded from environment variables named in `api_key_env`. You can use any variable name:

```yaml
generalist:
  api_key_env: "MY_CUSTOM_KEY_VAR"
```

```bash
export MY_CUSTOM_KEY_VAR="sk-..."
```

### Persisting API Keys

Add to your shell profile so they're available in every session:

```bash
# ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-..."
```

On Windows (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

---

## Custom Specialists

You can define any specialist with any name. The generalist routes to them by name.

### Example: Legal Specialist

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis.
    Route using: [ROUTE: return], [ROUTE: legal], [ROUTE: code]
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"

specialists:
  legal:
    system_prompt: |
      You are a legal research specialist.
      Provide general legal information (not legal advice).
      End with [RETURN].
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3

  code:
    system_prompt: |
      You are a code specialist.
      Generate clean, correct code.
      End with [RETURN].
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
```

### Example: Language Specialist

```yaml
specialists:
  translator:
    system_prompt: |
      You are a translation specialist.
      Translate text accurately, preserving tone and meaning.
      End with [RETURN].
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.3
```

---

## Controlling Temperature Per Task

Use low temperature for deterministic tasks and higher for creative ones:

```yaml
specialists:
  math:
    temperature: 0.1    # Very deterministic — math needs exact answers

  code:
    temperature: 0.2    # Low — consistent code style

  knowledge:
    temperature: 0.5    # Balanced — factual but natural language

  creative:
    temperature: 0.9    # High — varied, creative output
```

---

## Large Context Models

For tasks requiring large context (long documents, big codebases), use models with larger context windows:

```yaml
specialists:
  document_analyst:
    system_prompt: |
      You are a document analysis specialist.
      Read and analyze long documents carefully.
      End with [RETURN].
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"           # 128K context window
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3
```

---

## Offline / Air-Gapped Setup

For fully offline use with Ollama:

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Answer helpfully.
    Route: [ROUTE: return], [ROUTE: math], [ROUTE: code]
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  api_key_env: ""

specialists:
  math:
    system_prompt: "Math specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.2
    delegates_to: ["tool_use"]

  code:
    system_prompt: "Code specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["tool_use"]

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

Note: Web search and URL fetching tools will fail without internet. Math, file, date, memory, and code execution tools work fully offline.

---

## Multiple Configs for Different Contexts

Create separate configs for different use cases:

```bash
~/.config/openjarvis/
├── coding.yaml      # Code-focused setup with codellama
├── research.yaml    # Research setup with web search emphasis
├── writing.yaml     # Creative writing with high temperature
└── default.yaml     # General-purpose fallback
```

Switch between them:
```bash
export OJ_CONFIG=~/.config/openjarvis/coding.yaml
openjarvis

# or per-session:
openjarvis --config ~/.config/openjarvis/research.yaml
```

---

## Debugging Configuration

### Check Which Config Is Loaded

The startup message shows configuration errors. If no error appears, config loaded successfully.

### Test a Specific Provider

Run OpenJarvis and type a simple question. If the response comes back, the provider is working. If you see a connection error, check:

1. Is the `base_url` correct?
2. Is the API key set? (`echo $OPENAI_API_KEY`)
3. Is the model name correct for the provider?
4. For Ollama: is it running? (`ollama list`)

### Verbose Routing

Watch the routing indicators in the terminal output to see which specialists are being used:

```
  ↳ routing: generalist → math
  ↳ routing: math → tool_use
  ↳ routing: tool_use → math
  ↳ routing: math → generalist
```

If routing isn't happening as expected, review the generalist's system prompt routing instructions.

---

## See Also

- [Configuration Overview](overview.md) — All configuration fields
- [Specialists](specialists.md) — Specialist prompt engineering
- [Providers](providers.md) — Provider-specific setup
- [Troubleshooting](../troubleshooting.md) — Common issues
