# Frequently Asked Questions

---

## General Questions

### What is OpenJarvis?

OpenJarvis is an AI orchestrator that routes conversations through specialized language models. Instead of using a single model for everything, OpenJarvis uses a team of specialists optimized for different tasks (math, code, knowledge, creative writing, etc.).

### Is OpenJarvis free?

Yes, OpenJarvis itself is open source and free. However, you'll need to either:

1. **Use a cloud AI provider** (OpenAI, Groq, etc.) — these charge API fees
2. **Run models locally** with Ollama — completely free, but requires decent hardware

### Does OpenJarvis work offline?

Yes, if you use Ollama for all specialists. Configure all specialists to use `http://localhost:11434/v1` and OpenJarvis will work completely offline (after models are downloaded).

### What AI providers does OpenJarvis support?

Any OpenAI-compatible API, including:

- **Ollama** (local, free)
- **OpenAI** (GPT-4, GPT-4o-mini)
- **Groq** (fast inference, free tier)
- **Anthropic Claude** (via OpenRouter)
- **OpenRouter** (access to many models)
- **Custom servers** (including the jarvis server)

### Can I mix different providers?

Yes! You can use different providers for different specialists:

```yaml
generalist:
  base_url: "https://api.openai.com/v1"  # OpenAI

specialists:
  code:
    base_url: "http://localhost:11434/v1"  # Ollama
  
  knowledge:
    base_url: "https://api.groq.com/v1"  # Groq
```

---

## Installation & Setup

### Do I need Python installed?

No! OpenJarvis is distributed as a pre-built binary that includes everything you need.

### How do I get API keys?

- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Groq:** [console.groq.com/keys](https://console.groq.com/keys)
- **OpenRouter:** [openrouter.ai/keys](https://openrouter.ai/keys)
- **Ollama:** No API key needed (local)

### What hardware do I need for local models (Ollama)?

**Minimum:**
- 8 GB RAM
- 10 GB disk space (for models)

**Recommended:**
- 16+ GB RAM
- NVIDIA GPU with 6+ GB VRAM (faster inference)
- 50+ GB disk space (multiple models)

### Which models should I use?

**For beginners with Ollama:**
- `llama3` — Good all-around model
- `codellama` — Better for code tasks

**For cloud (OpenAI):**
- `gpt-4o-mini` — Fast, cheap, good quality
- `gpt-4o` — Best quality, more expensive

**For fast inference (Groq):**
- `llama-3.1-70b-versatile` — Fast and capable
- `llama-3.1-8b-instant` — Very fast, smaller model

---

## Usage Questions

### How do I know if specialists are being used?

You'll see routing messages:

```
  routing: generalist → math → tool_use
```

This shows the generalist routed to math, which delegated to tool_use.

### Why don't I see routing messages sometimes?

Simple questions are answered directly by the generalist without routing. Routing only happens when the generalist decides a specialist would do better.

### Do I need to explicitly ask for tools?

No! Specialists automatically use tools when needed. Just ask naturally:

❌ "Use the web_search tool to find..."  
✅ "What's the latest news about AI?"

### Can I force routing to a specific specialist?

Not currently. The generalist makes routing decisions. You can guide it with phrasing:

- "Calculate..." → More likely to route to math
- "Write code..." → More likely to route to code
- "Tell me about..." → More likely to route to knowledge

### How do I save conversation history?

Currently, conversation history only persists within a session. Cross-session memory is planned for a future release.

You can use the memory tools for important information:

```
> Save a note called "important": Remember to follow up on project X
```

---

## Configuration Questions

### What's the difference between temperature values?

- **0.0-0.3:** Deterministic, consistent (math, code)
- **0.4-0.7:** Balanced (general use)
- **0.8-1.0:** Creative, varied (writing)

### What does `delegates_to` do?

It controls which specialists a specialist can delegate to. For example:

```yaml
code:
  delegates_to: ["math", "tool_use"]
```

This allows the code specialist to:
- Delegate math problems to the math specialist
- Delegate tool execution to tool_use

### Do I need all 7 specialists?

No! You only need the generalist. Other specialists are optional:

```yaml
generalist:
  # ... config ...

specialists:
  math:
    # ... config ...
```

If you don't define a specialist, the generalist handles those tasks itself.

### Can I create custom specialists?

Yes! Add any specialist name to your config:

```yaml
specialists:
  legal:
    system_prompt: "You are a legal specialist..."
    base_url: "..."
    model: "..."
```

Then add it to the generalist's routing instructions.

---

## Troubleshooting Questions

### Why am I getting "Connection refused" errors?

**For Ollama:** Ollama isn't running. Start it:
```bash
ollama serve
```

**For cloud providers:** Check your internet connection and API URL.

### Why am I getting "Model not found" errors?

**For Ollama:**
```bash
ollama pull llama3
```

**For cloud providers:** Use a valid model name for that provider.

### Why are responses slow?

**Causes:**
1. Large models on slow hardware (Ollama)
2. Remote API latency
3. Multiple routing hops (complex queries)

**Solutions:**
- Use smaller/faster models
- Use Groq for fast inference
- This is normal for complex multi-hop queries

### Tools aren't working. Why?

Verify `delegates_to` includes `tool_use`:

```yaml
math:
  delegates_to: ["tool_use"]  # Required
```

---

## Security & Privacy Questions

### Is my data sent to third parties?

**With Ollama:** No, everything runs locally.

**With cloud providers:** Yes, your queries are sent to the provider's API. Check their privacy policy:
- [OpenAI Privacy Policy](https://openai.com/policies/privacy-policy)
- [Groq Privacy Policy](https://groq.com/privacy-policy)

### Is code execution safe?

**No** — the `run_python` and `run_shell` tools execute arbitrary code on your machine. Only use with trusted inputs or disable these tools.

### Can I disable certain tools?

Not currently, but this feature is planned for a future release.

### Where are my notes stored (memory tools)?

In `~/.openjarvis/notes/` as JSON files. These are local to your machine.

---

## Comparison Questions

### How is OpenJarvis different from ChatGPT?

**ChatGPT:** Single model handles everything

**OpenJarvis:** Orchestrates multiple specialized models

**Benefits of OpenJarvis:**
- Mix cloud and local models
- Better results for specialized tasks
- Full control and transparency
- Can run completely offline
- Open source

### How is OpenJarvis different from LangChain?

**LangChain:** Framework for building AI applications (requires coding)

**OpenJarvis:** Ready-to-use AI assistant (just configure and run)

LangChain is for developers building AI apps. OpenJarvis is for end users and can be used immediately.

### Should I use OpenJarvis or just Ollama?

**Just Ollama:** Direct model access, simpler

**OpenJarvis:** Intelligent routing, tool integration, multi-model orchestration

Use OpenJarvis if you want:
- Automatic tool use
- Multi-step reasoning across specialists
- Mix of local and cloud models

Use just Ollama if you want:
- Direct model access
- Simpler setup
- Single-model interaction

---

## Advanced Questions

### Can I add custom tools?

Not currently, but a plugin system is planned for a future release.

### How does routing work internally?

Models use text-based tags in their responses:

- `[ROUTE: math]` — Generalist routes to math specialist
- `[RETURN]` — Specialist returns to generalist
- `[DELEGATE: tool_use]` — Specialist delegates to tool_use

See [Routing Protocol](usage/routing.md) for details.

### What's the maximum routing depth?

Current limit: 20 hops (safety limit to prevent infinite loops)

### Can specialists talk to each other directly?

No. All routing goes through the generalist:

```
Specialist A → Generalist → Specialist B
```

Except for delegation (specialist → specialist) via `delegates_to`.

---

## Project Questions

### Is OpenJarvis actively maintained?

Yes, the project is under active development.

### What's the license?

MIT License — see the LICENSE file in the installation directory

### Where can I report bugs or request features?

[GitHub Issues](https://github.com/bhanuponguru/OpenJarvis/issues)

---

## Still Have Questions?

- **Documentation:** Browse the full docs (you're reading them!)
- **Troubleshooting:** [Troubleshooting Guide](troubleshooting.md)
- **GitHub:** [github.com/bhanuponguru/OpenJarvis](https://github.com/bhanuponguru/OpenJarvis)
- **Issues:** [Report bugs or ask questions](https://github.com/bhanuponguru/OpenJarvis/issues)
