# Frequently Asked Questions (FAQ)

---

## General Questions

### What is OpenJarvis?
OpenJarvis is an intelligent AI conductor that routes conversational queries to specialized language models (such as mathematics, coding, planning, or factual lookup) across any OpenAI-compatible provider.

### Is OpenJarvis free to use?
Yes, OpenJarvis is free and open-source under the MIT license. If you connect it to local inference servers like Ollama, there are zero subscription or API costs. If you connect it to cloud APIs (OpenAI, Groq, OpenRouter), you only pay standard usage rates to those providers.

### Does OpenJarvis work completely offline?
Yes! When configured with local backends like Ollama, all routing, math solving, code linting/execution, file reading/writing, and date arithmetic run 100% locally on your machine without internet access.

---

## Models & Providers

### Which providers are supported?
Any endpoint implementing the standard OpenAI `/v1/chat/completions` REST API, including:
- **Ollama** (local, private, free)
- **OpenAI** (`gpt-4o`, `gpt-4o-mini`, etc.)
- **Groq** (`llama-3.1-70b-versatile`, high-speed inference)
- **OpenRouter** (Claude 3.5, Gemini, Mistral)
- **vLLM / LM Studio / llama.cpp server**

### Can I mix cloud and local models in one session?
Yes! Each specialist in `specialists.yaml` can have its own `base_url`, `model`, `api_key_env`, and `temperature`. For example, you can use local Ollama for coding and OpenAI for general orchestration.

---

## Built-In Tools

### How many built-in tools are included?
OpenJarvis includes **49 production-ready tools** across 9 categories:
1. **File I/O (9)**: `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file`
2. **Git & Version Control (4)**: `git_diff`, `git_status`, `git_log`, `apply_patch`
3. **Web & API (5)**: `fetch_url`, `search_web`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec`
4. **Code Execution (4)**: `run_python`, `run_shell`, `lint_python`, `run_pytest`
5. **Code Editor & Terminal (3)**: `str_replace_editor`, `execute_bash`, `bash`
6. **Data Processing (6)**: `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query`
7. **Math (4)**: `evaluate_expression`, `convert_units`, `solve_equation`, `prime_factorize`
8. **Date & Time (4)**: `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between`
9. **Session & Memory (10)**: `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and backwards-compatible note storage aliases

### Do I need to tell OpenJarvis which tool to use?
No. OpenJarvis supplies native function schemas to the models. When a calculation, file inspection, or search is required, the model triggers the tool automatically.

---

## Configuration & Usage

### Where should I place my configuration file?
OpenJarvis searches in this order:
1. File pointed to by `OJ_CONFIG` environment variable
2. `./specialists.yaml` in current working directory
3. `~/.config/openjarvis/specialists.yaml`
4. `/etc/openjarvis/specialists.yaml`

If no configuration exists, OpenJarvis launches the setup wizard on first run.

### How do I insert multiple lines in the chat prompt?
Press `Escape` followed by `Enter` (or `Alt+Enter`) to insert a new line without submitting. Press `Enter` on its own when ready to submit.

---

## Support & Resources

- **GitHub Repository**: [github.com/bhanuponguru/openjarvis-cli](https://github.com/bhanuponguru/openjarvis-cli)
- **Issue Tracker**: [Report issues or request features](https://github.com/bhanuponguru/openjarvis-cli/issues)
- **Troubleshooting Guide**: [Troubleshooting Guide](troubleshooting.md)
