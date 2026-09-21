# Frequently Asked Questions (FAQ)

Technical reference answers for common architectural, configuration, and runtime questions.

---

## 1. System Architecture

### What is OpenJarvis CLI?
OpenJarvis CLI is an open-source, vendor-agnostic agentic orchestration engine and terminal client. It executes tasks by dispatching them across an asynchronous Multi-Agent System (MAS) of Conductor nodes, coordinated via message envelopes, neighbor consensus, and content-addressable artifact storage.

### How does the multi-agent hierarchy operate?
The root coordinator receives the user prompt and dynamically spawns worker conductors via `spawn_agent`. Peer agents establish communication links via `connect_agents`. Agents communicate via mailboxes and must respect a bottom-up exit hierarchy: child agents must terminate via `exit_agent` before their parent can terminate or signal `complete_task`.

### What is the runtime dependency footprint?
OpenJarvis CLI is pure Python (Python 3.13 / 3.14). It does not import or require PyTorch, CUDA, transformers, or GPU acceleration. Standalone binaries compiled via PyInstaller run without an external Python interpreter.

---

## 2. Providers & Models

### Which LLM providers and APIs are supported?
OpenJarvis connects to any provider exposing an OpenAI-compatible `/v1/chat/completions` REST interface or standard provider APIs:
- **Local Endpoints**: Ollama, vLLM, llama.cpp, LocalAI.
- **Cloud Providers**: OpenAI, Anthropic, Google Gemini, Groq, OpenRouter, Mistral, DeepSeek.

### Can different agents in the same session use different providers?
Yes. Each agent profile declared in `.openjarvis/config.yaml` can specify its own `provider`, `model`, `base_url`, `api_key_env`, `temperature`, and `max_tokens`. For instance, the root coordinator can use `gpt-4o`, a coding worker can run on Anthropic Claude 3.5 Sonnet, and a research worker can run against a local Ollama instance.

---

## 3. Built-In Tools & Permissions

### How many built-in tools are included?
OpenJarvis registers 49 deterministic built-in tools across 9 functional categories, plus 5 multi-agent coordination meta-tools:
1. **File Operations (9)**: `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file`
2. **Git & VCS (4)**: `git_status`, `git_diff`, `git_log`, `apply_patch`
3. **Web & Network (5)**: `search_web`, `fetch_url`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec`
4. **Code Execution (4)**: `run_python`, `run_shell`, `lint_python`, `run_pytest`
5. **Code Editor & Terminal (3)**: `str_replace_editor`, `execute_bash`, `bash`
6. **Data Processing (6)**: `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query`
7. **Math & Arithmetic (4)**: `evaluate_expression`, `solve_equation`, `convert_units`, `prime_factorize`
8. **Date & Time (4)**: `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between`
9. **Session Memory (10)**: `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and backwards-compatible note storage aliases (`store_note`, `recall_note`, `list_notes`, `delete_note`)
10. **Meta-Tools (5)**: `spawn_agent`, `connect_agents`, `report_findings`, `exit_agent`, `complete_task`

### How are tool permissions evaluated?
The `PermissionManager` enforces one of three operational modes (`interactive`, `autonomous`, `allowlist`). Meta-tools bypass confirmation prompts, while other tools are evaluated against blocklists, pattern rules (`argument_patterns` matched with `fnmatch`), allowlists, and optional safety classifier checks.

---

## 4. Configuration & Runtime

### Where does OpenJarvis search for configuration files?
Configuration files are resolved in the following priority:
1. Explicit CLI argument: `--config <path>`
2. Environment variable: `OJ_CONFIG`
3. Workspace configuration: `./.openjarvis/config.yaml`
4. User global configuration: `~/.openjarvis/config.yaml`
5. System configuration: `/etc/openjarvis/config.yaml`

If no configuration is located, the interactive setup wizard is invoked.

### How do multiline prompts work in the REPL?
In the interactive terminal, press `Escape` then `Enter` (or `Alt+Enter`) to insert a newline. Press `Enter` alone to submit the prompt.

### How do non-interactive / headless runs work?
Use `-p` or `--prompt` with `-y` or `--auto-approve` (or `--mode autonomous`):
```bash
openjarvis -y -p "Run pytest and lint checks on src/"
```
