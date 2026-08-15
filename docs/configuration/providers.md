# Provider Configuration

OpenJarvis works with any OpenAI-compatible API. This page covers setup for the most common providers.

---

## Ollama (Local, Free)

Ollama runs models on your own machine — no API key, no cost, no data leaving your device.

### Setup

1. Install Ollama: [ollama.ai](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3
   ollama pull codellama
   ```
3. Start Ollama (usually starts automatically):
   ```bash
   ollama serve
   ```

### Configuration

```yaml
generalist:
  system_prompt: "..."
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  api_key_env: ""          # No key needed
  temperature: 0.7

specialists:
  code:
    system_prompt: "..."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["tool_use"]
```

### Available Models

| Model | Size | Best For |
|-------|------|---------|
| `llama3` | 8B | General use |
| `llama3:70b` | 70B | Higher quality (needs 40GB+ RAM) |
| `codellama` | 7B | Code generation |
| `codellama:13b` | 13B | Better code quality |
| `mistral` | 7B | Fast, general use |
| `deepseek-coder` | 7B | Excellent for code |
| `phi3` | 3.8B | Very fast, lightweight |

Check all available models: `ollama list`
Browse more: `ollama search <keyword>`

### Hardware Requirements

| Model Size | Min RAM | GPU VRAM |
|-----------|---------|----------|
| 3-4B | 8 GB | 4 GB |
| 7-8B | 16 GB | 6 GB |
| 13B | 32 GB | 10 GB |
| 70B | 64 GB | 40 GB |

Running without a GPU works but is much slower (CPU inference).

---

## OpenAI

### Setup

1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Generate an API key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

### Configuration

```yaml
generalist:
  system_prompt: "..."
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  code:
    system_prompt: "..."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: ["tool_use"]
```

### Available Models

| Model | Speed | Quality | Cost |
|-------|-------|---------|------|
| `gpt-4o-mini` | Fast | Good | Low |
| `gpt-4o` | Medium | Excellent | Medium |
| `gpt-4-turbo` | Medium | Excellent | Medium |
| `o1-mini` | Slow | Best reasoning | High |

**Recommendation:** Use `gpt-4o-mini` for most specialists — it's fast and cost-effective. Use `gpt-4o` for the generalist if you need higher quality routing decisions.

---

## Groq

Groq offers extremely fast inference (often 10-20x faster than OpenAI) with a free tier.

### Setup

1. Create an account at [console.groq.com](https://console.groq.com)
2. Generate an API key at [console.groq.com/keys](https://console.groq.com/keys)
3. Set the environment variable:
   ```bash
   export GROQ_API_KEY="gsk_..."
   ```

### Configuration

```yaml
generalist:
  system_prompt: "..."
  base_url: "https://api.groq.com/openai/v1"
  model: "llama-3.1-70b-versatile"
  api_key_env: "GROQ_API_KEY"
  temperature: 0.7
```

### Available Models

| Model | Speed | Context |
|-------|-------|---------|
| `llama-3.1-8b-instant` | Extremely fast | 128K |
| `llama-3.1-70b-versatile` | Very fast | 128K |
| `mixtral-8x7b-32768` | Fast | 32K |
| `gemma2-9b-it` | Fast | 8K |

**Recommendation:** `llama-3.1-70b-versatile` gives excellent quality at very high speed.

---

## OpenRouter

OpenRouter provides access to many models (including Claude, Gemini, and others) through a single API.

### Setup

1. Create an account at [openrouter.ai](https://openrouter.ai)
2. Generate an API key at [openrouter.ai/keys](https://openrouter.ai/keys)
3. Set the environment variable:
   ```bash
   export OPENROUTER_API_KEY="sk-or-..."
   ```

### Configuration

```yaml
generalist:
  system_prompt: "..."
  base_url: "https://openrouter.ai/api/v1"
  model: "anthropic/claude-3-5-haiku"
  api_key_env: "OPENROUTER_API_KEY"
  temperature: 0.7
```

### Popular Models via OpenRouter

| Model ID | Provider |
|----------|---------|
| `anthropic/claude-3-5-sonnet` | Anthropic Claude |
| `anthropic/claude-3-5-haiku` | Anthropic Claude (fast) |
| `google/gemini-pro-1.5` | Google Gemini |
| `meta-llama/llama-3.1-405b` | Meta Llama |
| `mistralai/mistral-large` | Mistral |

See all models at [openrouter.ai/models](https://openrouter.ai/models).

---

## Mixing Providers

You can use different providers for different specialists. This lets you optimize for cost, speed, and quality per task.

### Example: Hybrid Setup

```yaml
generalist:
  # OpenAI for smart routing decisions
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  math:
    # Local Ollama for privacy
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    api_key_env: ""
    temperature: 0.2
    delegates_to: ["tool_use"]

  code:
    # Groq for speed
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  knowledge:
    # OpenAI for accuracy
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.5
    delegates_to: ["tool_use"]

  tool_use:
    # Ollama for free tool execution
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    api_key_env: ""
    temperature: 0.3
```

---

## Custom / Self-Hosted Servers

Any server that implements the OpenAI Chat Completions API works.

```yaml
generalist:
  system_prompt: "..."
  base_url: "http://your-server:8080/v1"
  model: "your-model-name"
  api_key_env: "YOUR_API_KEY"   # or "" if no auth
  temperature: 0.7
```

This works with vLLM, LM Studio, llama.cpp server, and other compatible backends.

---

## See Also

- [Configuration Overview](overview.md) — All configuration fields
- [Specialists](specialists.md) — Specialist-specific setup
- [Advanced Configuration](advanced.md) — Multiple configs, env overrides
