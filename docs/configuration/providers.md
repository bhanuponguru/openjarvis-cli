# Provider Configuration

OpenJarvis supports all LLM providers backed by LangChain, including local inference via Ollama, cloud providers (OpenAI, Anthropic, Google Gemini, Groq, OpenRouter), and custom OpenAI-compatible endpoints.

---

## 1. Supported Providers

| Provider | `provider` Field | Default Model | Environment Variable |
|----------|-----------------|---------------|----------------------|
| **Ollama** (Local) | `ollama` | `llama3` | None (Local, Free) |
| **OpenAI** | `openai` | `gpt-4o` | `OPENAI_API_KEY` |
| **Anthropic** | `anthropic` | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| **Google Gemini** | `google` | `gemini-1.5-pro` | `GOOGLE_API_KEY` |
| **Custom / Groq / OpenRouter** | `custom` or `openai` | User-defined | User-defined |

---

## 2. Ollama (Local, Private, Free)

Ollama runs models directly on your hardware without transmitting data to external APIs.

```yaml
generalist:
  name: "generalist"
  system_prompt: "You are the router."
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "llama3"
  temperature: 0.7
```

---

## 3. Anthropic (Claude)

```yaml
generalist:
  name: "generalist"
  system_prompt: "You are the router."
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"
  temperature: 0.2
```

---

## 4. Google Gemini

```yaml
generalist:
  name: "generalist"
  system_prompt: "You are the router."
  provider: "google"
  model: "gemini-1.5-pro"
  api_key_env: "GOOGLE_API_KEY"
  temperature: 0.0
```

---

## 5. OpenAI

```yaml
generalist:
  name: "generalist"
  system_prompt: "You are the router."
  provider: "openai"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.0
```

---

## 6. Groq / OpenRouter / Custom Endpoints

Any OpenAI-compatible server (vLLM, LM Studio, Groq, OpenRouter) can be connected using `provider: "custom"` or `provider: "openai"` with `base_url`:

```yaml
specialists:
  fast_coder:
    name: "fast_coder"
    system_prompt: "You write fast code."
    provider: "custom"
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.0
```

---

## 7. Hybrid Multi-Provider Setup

You can configure different providers for different specialists. For example, use Claude for complex architecture, Groq for fast code generation, and local Ollama for mathematics:

```yaml
generalist:
  name: "generalist"
  system_prompt: "Router"
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"

specialists:
  math:
    name: "math"
    system_prompt: "Math expert"
    provider: "ollama"
    base_url: "http://localhost:11434"
    model: "llama3"

  code:
    name: "code"
    system_prompt: "Coding specialist"
    provider: "custom"
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.1-70b-versatile"
    api_key_env: "GROQ_API_KEY"
```
