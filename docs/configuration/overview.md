# Configuration Overview

OpenJarvis uses a YAML configuration file to define specialists and their behavior.

---

## Configuration File Location

OpenJarvis looks for configuration in this order:

1. File specified with `--config` flag: `openjarvis --config my-config.yaml`
2. `OJ_CONFIG` environment variable: `export OJ_CONFIG=/path/to/config.yaml`
3. `specialists.yaml` in current directory
4. `~/.config/openjarvis/specialists.yaml`

---

## Basic Structure

```yaml
generalist:
  system_prompt: "..."
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  math:
    system_prompt: "..."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
    delegates_to: ["tool_use"]
  
  code:
    system_prompt: "..."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]
```

---

## Configuration Sections

### Generalist (Required)

The conductor that routes requests and synthesizes final answers.

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Route requests using:
    [ROUTE: return] - Final answer
    [ROUTE: math] - Math tasks
    [ROUTE: code] - Code tasks
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7
```

### Specialists (Optional)

Domain-specific models for specialized tasks.

```yaml
specialists:
  math:
    system_prompt: "..."
    base_url: "..."
    model: "..."
    temperature: 0.3
    delegates_to: ["tool_use"]
```

---

## Field Reference

### system_prompt (required)

Instructions for the model. For the generalist, must include routing tags. For specialists, must include `[RETURN]` instruction.

**Example:**
```yaml
system_prompt: |
  You are a math specialist.
  Solve problems step-by-step.
  End with [RETURN] to send back to generalist.
```

### base_url (required)

API endpoint URL. Common values:

- OpenAI: `https://api.openai.com/v1`
- Ollama: `http://localhost:11434/v1`
- Groq: `https://api.groq.com/v1`
- Claude (via OpenRouter): `https://openrouter.ai/api/v1`

### model (required)

Model identifier. Depends on your provider:

**OpenAI:**
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`

**Ollama:**
- `llama3`
- `llama3:70b`
- `codellama`
- `mistral`

**Groq:**
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`

### api_key_env (optional)

Name of environment variable containing the API key.

**Example:**
```yaml
api_key_env: "OPENAI_API_KEY"
```

Set the environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

Leave empty for providers that don't need authentication (Ollama):
```yaml
api_key_env: ""
```

### temperature (optional, default: 0.7)

Controls randomness in model output:

- **0.0-0.3:** Deterministic, focused (good for math, code)
- **0.4-0.7:** Balanced (good for general use)
- **0.8-1.0:** Creative, diverse (good for writing)

**Example:**
```yaml
math:
  temperature: 0.2  # Precise calculations

creative:
  temperature: 0.9  # Diverse creative output
```

### delegates_to (optional)

List of specialists this specialist can delegate to.

**Example:**
```yaml
code:
  delegates_to: ["math", "tool_use"]
```

This allows the code specialist to:
- Delegate math problems to the math specialist
- Delegate tool execution to the tool_use specialist

---

## Example Configurations

### Fully Local (Ollama)

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Route using:
    [ROUTE: return], [ROUTE: math], [ROUTE: code], [ROUTE: knowledge]
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  api_key_env: ""
  temperature: 0.7

specialists:
  math:
    system_prompt: "Math specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    system_prompt: "Code specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

### Cloud Only (OpenAI)

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis. Route using routing tags.
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  math:
    system_prompt: "Math specialist. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    system_prompt: "Code specialist. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3
```

### Hybrid (Best Model for Each Task)

```yaml
generalist:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  math:
    base_url: "http://localhost:11434/v1"
    model: "llama3"  # Local for privacy
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    base_url: "https://api.groq.com/v1"
    model: "llama-3.1-70b-versatile"  # Groq for speed
    api_key_env: "GROQ_API_KEY"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  knowledge:
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"  # OpenAI for accuracy
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.5
    delegates_to: ["tool_use"]

  tool_use:
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

---

## Environment Variables

### API Keys

Set API keys as environment variables:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Groq
export GROQ_API_KEY="gsk_..."

# Anthropic (via OpenRouter)
export OPENROUTER_API_KEY="sk-or-..."
```

Add to your shell profile for persistence:

```bash
# ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY="sk-..."
```

### Config Path

Override default config location:

```bash
export OJ_CONFIG="/path/to/my-config.yaml"
```

---

## Validation

OpenJarvis validates your configuration on startup. Common errors:

### Missing Required Field

```
Error: Missing required field 'base_url' for specialist 'math'
```

**Fix:** Add the missing field to your config.

### Invalid URL

```
Error: Invalid base_url 'not-a-url' for generalist
```

**Fix:** Use a proper URL (must start with `http://` or `https://`).

### Missing API Key

```
Error: Environment variable 'OPENAI_API_KEY' not set
```

**Fix:** Set the API key:
```bash
export OPENAI_API_KEY="sk-..."
```

### Invalid Delegation

```
Error: Specialist 'code' delegates to unknown specialist 'unknown'
```

**Fix:** Only delegate to specialists that exist in your config.

---

## Next Steps

- **[Specialists Configuration →](specialists.md)** — Detailed specialist setup
- **[Providers Configuration →](providers.md)** — Provider-specific guides
- **[Advanced Configuration →](advanced.md)** — Power user features

---

## See Also

- [Quick Start](../getting-started/quick-start.md) — Example configurations
- [Troubleshooting](../troubleshooting.md) — Common config issues
