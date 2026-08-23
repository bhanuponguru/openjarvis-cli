# Troubleshooting Guide

Solutions and diagnostic steps for common issues encountered when using OpenJarvis.

---

## 1. Startup & Setup Issues

### Setup Wizard Launches Unexpectedly
**Symptom:** OpenJarvis enters the 3-step interactive setup wizard instead of the chat prompt.
- **Cause:** No configuration file was found at `OJ_CONFIG`, `./specialists.yaml`, `~/.config/openjarvis/specialists.yaml`, or `/etc/openjarvis/specialists.yaml`.
- **Fix:** Complete the wizard to generate `~/.config/openjarvis/specialists.yaml`, or set `OJ_CONFIG=/path/to/specialists.yaml`.

### Missing API Key Error
**Symptom:** `Environment variable 'OPENAI_API_KEY' is not set.`
- **Cause:** The active specialist configuration specifies `api_key_env: "OPENAI_API_KEY"`, but the variable is unset in the current shell environment.
- **Fix:** Export the variable in your shell:
  ```bash
  export OPENAI_API_KEY="sk-..."
  ```

### Invalid YAML or Unknown Fields
**Symptom:** OpenJarvis prints a configuration validation error on startup.
- **Cause:** Typo in field names or malformed YAML indentation.
- **Fix:** Ensure allowed fields are used: `name`, `system_prompt`, `provider`, `base_url`, `model`, `api_key_env`, `temperature`, `max_tokens`, `stop`, `timeout`, `delegates_to`.

---

## 2. Provider Connection Issues

### Connection Refused (Ollama / Local Endpoints)
**Symptom:** `Cannot connect to host localhost:11434`
- **Cause:** Ollama or the local inference engine is not running.
- **Fix:** Start Ollama:
  ```bash
  ollama serve
  ```
  Verify available models with `ollama list`.

### Model Not Found
**Symptom:** Provider returns 404 Model Not Found.
- **Cause:** The model name specified in `model:` has not been pulled or does not exist on the provider account.
- **Fix:** Pull the model (e.g. `ollama pull llama3`) or verify the model ID on OpenAI/Groq/OpenRouter.

---

## 3. Tool & Function Calling Issues

### Web Search Returns Empty Results
**Symptom:** `search_web` yields no results.
- **Cause:** Temporary network disconnection or rate limiting from the search engine.
- **Fix:** Verify internet access or retry after a few moments.

### Subprocess Timeout on Code Execution
**Symptom:** `run_python` or `run_shell` times out.
- **Cause:** The script executed an infinite loop, blocked on input, or took longer than 10-15 seconds.
- **Fix:** Keep code execution snippets self-contained, non-interactive, and concise.

---

## 4. Routing & Specialist Behaviour

### Generalist Never Routes to Specialists
**Symptom:** The generalist answers every question directly without delegating.
- **Cause:** The generalist system prompt does not clearly explain the specialist tags or has a high temperature.
- **Fix:** Ensure `system_prompt` lists `[ROUTE: <specialist>]` explicitly and `temperature` is set to `0.0`.

### Reaching Maximum Hops
**Symptom:** A prompt stops after 10 hops without concluding.
- **Cause:** Specialists are delegating back and forth without emitting `[RETURN]`.
- **Fix:** Review specialist system prompts to ensure each prompt instructs the model: `End your answer with [RETURN].`

---

## See Also

- [Quick Start Guide](getting-started/quick-start.md) — Getting started
- [Configuration Overview](configuration/overview.md) — Config reference
- [Built-in Tools](tools/overview.md) — Built-in tools inventory
