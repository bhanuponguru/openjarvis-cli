# Provider Configuration

OpenJarvis supports local and cloud LLM backends via LangChain integrations, including local inference engines, commercial APIs, and custom OpenAI-compatible endpoints.

---

## 1. Supported Providers

| Provider Identifier | Backend Class | Default Base URL | Credential Variable |
| :--- | :--- | :--- | :--- |
| **`ollama`** | `ChatOllama` | `http://localhost:11434` | None (Local) |
| **`openai`** | `ChatOpenAI` | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| **`anthropic`** | `ChatAnthropic` | `https://api.anthropic.com` | `ANTHROPIC_API_KEY` |
| **`google`** | `ChatGoogleGenerativeAI` | Default Google API endpoint | `GOOGLE_API_KEY` |
| **`custom`** | `ChatOpenAI` | User configured `base_url` | User configured `api_key_env` |

---

## 2. Ollama (Local & Offline)

Connects to a locally running Ollama daemon:

```yaml
root_agent:
  name: "root"
  role: "coordinator"
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "llama3.1"
  temperature: 0.1

agents:
  coder:
    role: "coder"
    provider: "ollama"
    base_url: "http://localhost:11434"
    model: "qwen2.5-coder:7b"
    temperature: 0.0
```

Start the Ollama daemon and pull the target models before running OpenJarvis:
```bash
ollama serve
ollama pull llama3.1
ollama pull qwen2.5-coder:7b
```

---

## 3. OpenAI

Connects to OpenAI API endpoints using `ChatOpenAI`:

```yaml
root_agent:
  name: "root"
  role: "coordinator"
  provider: "openai"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.1
```

Set the API key in your shell:
```bash
export OPENAI_API_KEY="sk-..."
```

---

## 4. Anthropic (Claude)

Connects to Anthropic API endpoints using `ChatAnthropic`:

```yaml
agents:
  coder:
    name: "coder"
    role: "coder"
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    api_key_env: "ANTHROPIC_API_KEY"
    temperature: 0.1
```

Set the API key in your shell:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 5. Google Gemini

Connects to Google Generative AI endpoints using `ChatGoogleGenerativeAI`:

```yaml
agents:
  researcher:
    name: "researcher"
    role: "researcher"
    provider: "google"
    model: "gemini-1.5-pro"
    api_key_env: "GOOGLE_API_KEY"
    temperature: 0.0
```

Set the API key in your shell:
```bash
export GOOGLE_API_KEY="AIza..."
```

---

## 6. Custom & OpenAI-Compatible Endpoints (vLLM, Groq, OpenRouter)

Any backend exposing standard `/v1/chat/completions` can be declared with `provider: "custom"` (or `provider: "openai"`):

### Groq
```yaml
agents:
  fast_coder:
    name: "fast_coder"
    role: "coder"
    provider: "custom"
    base_url: "https://api.groq.com/openai/v1"
    model: "llama-3.3-70b-versatile"
    api_key_env: "GROQ_API_KEY"
    temperature: 0.0
```

### OpenRouter
```yaml
agents:
  reasoner:
    name: "reasoner"
    role: "coordinator"
    provider: "custom"
    base_url: "https://openrouter.ai/api/v1"
    model: "deepseek/deepseek-r1"
    api_key_env: "OPENROUTER_API_KEY"
    temperature: 0.0
```

### Local vLLM Server
```yaml
agents:
  local_worker:
    name: "local_worker"
    role: "coder"
    provider: "custom"
    base_url: "http://localhost:8000/v1"
    model: "Qwen/Qwen2.5-Coder-32B-Instruct"
    temperature: 0.0
```

---

## 7. Heterogeneous Multi-Provider Configuration

Different agents in the same session can utilize distinct providers and models tailored to specific roles:

```yaml
root_agent:
  name: "root"
  role: "coordinator"
  provider: "openai"
  model: "gpt-4o"
  api_key_env: "OPENAI_API_KEY"

agents:
  coder:
    name: "coder"
    role: "coder"
    provider: "anthropic"
    model: "claude-3-5-sonnet-20241022"
    api_key_env: "ANTHROPIC_API_KEY"

  researcher:
    name: "researcher"
    role: "researcher"
    provider: "google"
    model: "gemini-1.5-pro"
    api_key_env: "GOOGLE_API_KEY"

  math:
    name: "math"
    role: "math"
    provider: "ollama"
    base_url: "http://localhost:11434"
    model: "llama3.1"
```
