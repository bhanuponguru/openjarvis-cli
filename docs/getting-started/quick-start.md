# Quick Start

Get OpenJarvis up and running in 5 minutes.

---

## Step 1: Install OpenJarvis

If you haven't already, [install OpenJarvis](installation.md) via binary or source.

---

## Step 2: Choose Your AI Provider

OpenJarvis works with any OpenAI-compatible API. Pick one:

### Option A: Ollama (Local, Free, Private)

**Best for:** Privacy, offline use, no API costs

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3
ollama pull codellama

# Start Ollama (runs in background)
ollama serve
```

**No API key needed!** Ollama runs completely on your machine.

### Option B: OpenAI (Cloud, Paid)

**Best for:** Highest quality, fastest setup

```bash
# Set your API key
export OPENAI_API_KEY="sk-..."
```

Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### Option C: Groq (Cloud, Free Tier)

**Best for:** Fast inference, generous free tier

```bash
# Set your API key
export GROQ_API_KEY="gsk_..."
```

Get an API key from [console.groq.com/keys](https://console.groq.com/keys).

---

## Step 3: Create Configuration File

Create `specialists.yaml` in your current directory:

### For Ollama (Local)

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis, an intelligent AI assistant.
    Route requests using these tags (on their own line):
    [ROUTE: return] - Send as final answer to user
    [ROUTE: math] - Route to math specialist
    [ROUTE: code] - Route to code specialist  
    [ROUTE: knowledge] - Route to knowledge specialist
    [ROUTE: creative] - Route to creative specialist
    [ROUTE: planning] - Route to planning specialist
    [ROUTE: tool_use] - Route to tool specialist
  base_url: "http://localhost:11434/v1"
  model: "llama3"
  api_key_env: ""
  temperature: 0.7

specialists:
  math:
    system_prompt: "You are a mathematics specialist. Solve problems step-by-step. End responses with [RETURN] to send back to the generalist."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    system_prompt: "You are a code specialist. Generate clean, well-documented code. End responses with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "codellama"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  knowledge:
    system_prompt: "You are a knowledge specialist. Provide accurate, well-researched information. End responses with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.5
    delegates_to: ["tool_use"]

  creative:
    system_prompt: "You are a creative specialist for writing and brainstorming. End responses with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.9

  planning:
    system_prompt: "You are a planning specialist for task decomposition. End responses with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.6
    delegates_to: ["knowledge", "math"]

  tool_use:
    system_prompt: "You are a tool specialist. Execute tools to gather information and perform actions. End responses with [RETURN]."
    base_url: "http://localhost:11434/v1"
    model: "llama3"
    temperature: 0.3
```

### For OpenAI (Cloud)

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis, an intelligent AI assistant.
    Route requests using these tags (on their own line):
    [ROUTE: return] - Send as final answer
    [ROUTE: math] - Route to math specialist
    [ROUTE: code] - Route to code specialist
    [ROUTE: knowledge] - Route to knowledge specialist
    [ROUTE: creative] - Route to creative specialist
    [ROUTE: planning] - Route to planning specialist
    [ROUTE: tool_use] - Route to tool specialist
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key_env: "OPENAI_API_KEY"
  temperature: 0.7

specialists:
  math:
    system_prompt: "Math specialist. Solve problems step-by-step. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3
    delegates_to: ["tool_use"]

  code:
    system_prompt: "Code specialist. Generate clean code. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.2
    delegates_to: ["math", "tool_use"]

  knowledge:
    system_prompt: "Knowledge specialist. Provide accurate information. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.5
    delegates_to: ["tool_use"]

  creative:
    system_prompt: "Creative specialist for writing. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.9

  planning:
    system_prompt: "Planning specialist for task decomposition. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.6
    delegates_to: ["knowledge", "math"]

  tool_use:
    system_prompt: "Tool specialist. Execute tools to gather information. End with [RETURN]."
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
    api_key_env: "OPENAI_API_KEY"
    temperature: 0.3
```

---

## Step 4: Run OpenJarvis

```bash
openjarvis
```

You should see:

```
OpenJarvis  (type 'exit' or 'quit' to stop)

> 
```

---

## Step 5: Try It Out

### Simple Question

```
> What is 15 squared?

  routing: generalist → math → tool_use
  routing: tool_use → math → generalist

15 squared is 225.
```

### Web Search

```
> What's the latest news about AI?

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → generalist

[Search results and summary appear here]
```

### Code Generation

```
> Write a Python function to validate email addresses

  routing: generalist → code
  routing: code → generalist

Here's a function to validate email addresses:

[Code appears here]
```

### Multi-Step Query

```
> Find Japan's GDP and calculate its square root

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → math → tool_use
  routing: tool_use → math → generalist

Japan's GDP is approximately $4.2 trillion.
The square root is approximately $2.05 million.
```

---

## Understanding the Output

### Routing Messages

```
  routing: generalist → math → tool_use
```

This shows the chain of specialists that handled your request:
1. **generalist** received your question
2. Routed to **math** specialist
3. **math** delegated to **tool_use** to execute calculator

### Final Answer

Everything after the routing messages is your answer — the routing tags have been automatically removed.

---

## Command-Line Options

```bash
# Use a different config file
openjarvis --config my-config.yaml

# Enable streaming (real-time output)
openjarvis --stream

# Verbose logging
openjarvis --verbose

# Show version
openjarvis --version

# Show help
openjarvis --help
```

---

## Tips for Better Results

### Be Specific

❌ "Tell me about Python"  
✅ "Explain Python list comprehensions with examples"

### Use Natural Language

You don't need special commands. Just ask naturally:

- "What's the weather in Tokyo?"
- "Write a function to sort a list"
- "Explain how transformers work"
- "Search for papers on quantum computing"

### Tools Activate Automatically

You don't need to explicitly call tools. OpenJarvis specialists automatically use tools when needed:

```
> What's 15% of 1000?
```

The **math** specialist automatically uses the `calculate` tool.

```
> What's the latest news about SpaceX?
```

The **knowledge** specialist automatically uses the `web_search` tool.

---

## Next Steps

- **[Configuration Guide →](../configuration/overview.md)** — Customize your setup
- **[Built-in Tools →](../tools/overview.md)** — See all 29 available tools
- **[Routing Protocol →](../usage/routing.md)** — Understand how routing works
- **[Python API →](../usage/python-api.md)** — Use OpenJarvis in your code

---

## Common Issues

### "Model not found" error

**Problem:** Ollama model not downloaded

**Solution:**
```bash
ollama pull llama3
ollama pull codellama
```

### "API key not found" error

**Problem:** API key not set

**Solution:**
```bash
export OPENAI_API_KEY="sk-..."
# Or add to ~/.bashrc or ~/.zshrc
```

### Specialists not routing correctly

**Problem:** System prompts don't match expected format

**Solution:** Use the example configs above exactly as written. The routing tags MUST be on their own line.

For more help, see [Troubleshooting](../troubleshooting.md).
