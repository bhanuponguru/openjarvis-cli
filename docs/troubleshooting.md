# Troubleshooting Guide

Diagnostic procedures and solutions for common runtime, configuration, and multi-agent execution issues in OpenJarvis CLI.

---

## 1. Startup & Configuration Issues

### Setup Wizard Launches Unexpectedly
**Symptom:** OpenJarvis enters the interactive setup wizard instead of loading the session.
- **Cause:** No configuration file was located at any standard path (`OJ_CONFIG`, `.openjarvis/config.yaml`, `~/.openjarvis/config.yaml`, or `/etc/openjarvis/config.yaml`).
- **Resolution:** Run through the wizard to generate `~/.openjarvis/config.yaml`, or specify an explicit config file via `--config <path>` or `OJ_CONFIG=<path>`.

### Missing API Key
**Symptom:** `ValueError: Environment variable 'OPENAI_API_KEY' is not set.`
- **Cause:** The configured provider requires an API key, but the referenced environment variable is unset.
- **Resolution:** Export the required key in your shell:
  ```bash
  export OPENAI_API_KEY="sk-..."
  # Or for other providers:
  export ANTHROPIC_API_KEY="sk-ant-..."
  export GEMINI_API_KEY="..."
  ```

### Invalid Configuration Schema
**Symptom:** OpenJarvis exits with a YAML validation or missing field error on startup.
- **Cause:** Typo in field names, invalid structure, or deprecated config keys.
- **Resolution:** Validate `.openjarvis/config.yaml` against the schema. Root-level keys are: `version`, `default_provider`, `default_model`, `root_agent`, `agents`, `tool_permissions`, and `providers`.

---

## 2. Multi-Agent System (MAS) Lifecycle Issues

### Parent Conductor Blocked by Active Child Agents
**Symptom:** The coordinator or parent agent attempts to finish but the engine reports active child agents.
- **Cause:** OpenJarvis enforces a strict **bottom-up exit hierarchy**. A parent agent cannot terminate while child agents spawned via `spawn_agent` remain active.
- **Resolution:** Ensure child agents call `exit_agent` upon task completion before the parent calls `exit_agent` or `complete_task`. The root coordinator must await findings from child nodes before emitting `complete_task`.

### Headless or CI Execution Blocks on Confirmation
**Symptom:** OpenJarvis hangs indefinitely in a headless environment, script, or CI/CD runner.
- **Cause:** The default permission mode is `interactive`, which expects stdin input for tool confirmation prompts. In a non-interactive shell, reading from stdin blocks.
- **Resolution:** Pass `-y` or `--auto-approve` (or set `--mode autonomous`) for unattended or script-driven invocations:
  ```bash
  openjarvis -y -p "Run pytest and generate coverage report"
  ```

### Child Agent Unconnected to Peer
**Symptom:** An agent attempts to send a message to another agent but the envelope delivery fails.
- **Cause:** Communication channels between peer agents must be established in the topology before direct messaging.
- **Resolution:** Use `connect_agents` with `agent_a` and `agent_b` to establish bidirectional communication edges prior to inter-agent message passing.

---

## 3. Provider & Network Connectivity

### Connection Refused (Local Ollama / vLLM Endpoints)
**Symptom:** `httpx.ConnectError: Cannot connect to host localhost:11434` or `localhost:8000`.
- **Cause:** The local inference server is stopped or listening on a different port.
- **Resolution:** Verify the server is running:
  ```bash
  # Check Ollama
  curl http://localhost:11434/api/tags
  # Or start Ollama
  ollama serve
  ```
  Ensure `base_url` in `.openjarvis/config.yaml` matches the listening port.

### HTTP 429 (Rate Limiting / Quota Exhaustion)
**Symptom:** Provider returns `429 Too Many Requests`.
- **Cause:** Multiple concurrent agent nodes calling cloud provider endpoints concurrently, exceeding provider TPM (Tokens Per Minute) or RPM (Requests Per Minute) quotas.
- **Resolution:** Configure lower concurrency, switch non-critical worker agents to local models (e.g. Ollama), or reduce token limits in agent profiles.

---

## 4. Built-in Tool Execution

### Subprocess Timeout on Code Execution
**Symptom:** `run_python`, `run_pytest`, or `bash` returns a timeout error.
- **Cause:** The invoked command exceeded the default 30-second execution deadline (e.g., interactive prompts, long builds, network hangs).
- **Resolution:** Provide non-interactive flags (e.g., `pytest -q`, `npm install --no-audit`), ensure commands terminate deterministically, or configure timeouts where applicable.

### Tool Execution Denied by Permission Policy
**Symptom:** `Permission denied: Tool '<tool_name>' is blocked by security policy`.
- **Cause:** The tool is listed under `blocked_tools`, violates an argument pattern rule, or is rejected in `allowlist` mode.
- **Resolution:** Check `.openjarvis/config.yaml` under `tool_permissions` and `.openjarvis/config/permissions.yaml`. Adjust `allowed_tools` or update argument pattern rules.

---

## See Also

- [Quick Start Guide](getting-started/quick-start.md)
- [Configuration Overview](configuration/overview.md)
- [Multi-Agent Topology & Consensus](usage/routing.md)
- [Security & Permissions](security.md)
- [CLI Reference](usage/cli.md)
