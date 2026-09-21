# Built-In Tools Overview

OpenJarvis includes **49 production-ready tools** organized into 9 functional modules. Models automatically invoke these tools using standard function calling.

---

## Tool Categories

| Module | Count | Available Tools |
| :--- | :--- | :--- |
| **[Date & Time](datetime.md)** | 4 | `get_current_datetime`, `date_arithmetic`, `format_datetime`, `days_between` |
| **[Math](math.md)** | 4 | `evaluate_expression`, `convert_units`, `solve_equation`, `prime_factorize` |
| **[File I/O](files.md)** | 9 | `read_file`, `write_file`, `list_directory`, `search_in_files`, `file_info`, `delete_file`, `search_dir`, `search_file`, `find_file` |
| **[Web](web.md)** | 5 | `fetch_url`, `search_web`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec` |
| **[Code Execution](code.md)** | 4 | `run_python`, `run_shell`, `lint_python`, `run_pytest` |
| **[Data Processing](data.md)** | 6 | `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query` |
| **[Session & Memory](memory.md)** | 10 | `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, `store_note`, `recall_note`, `list_notes`, `delete_note` |
| **[Code Editor & Terminal](editor.md)** | 3 | `str_replace_editor`, `execute_bash`, `bash` |
| **[Git & Version Control](git.md)** | 4 | `git_diff`, `git_status`, `git_log`, `apply_patch` |

**Total: 49 Built-in Tools**

---

## How Tool Calling Works

1. **Automatic Detection**: When a user's request requires calculations, web lookups, or file inspection, the active model outputs a structured tool call.
2. **Execution & Feedback**: OpenJarvis runs the tool locally (sandboxed subprocess for code, safe AST evaluator for math) and returns the result to the model.
3. **Synthesis**: The model uses the tool output to complete its answer and returns it to you.

```text
oj> What's the square root of 1764 plus 58?

  [agent-math] ⚙ evaluate_expression {"expression": "1764**0.5 + 58"}
    → 100.0

The square root of 1764 (42) plus 58 is **100**.
```

---

## Tool Safety & Guardrails

- **Math Evaluation (`evaluate_expression`)**: Evaluates math expressions safely using AST parsing (no `eval()` or code execution).
- **Code Execution (`run_python`, `run_shell`)**: Runs in isolated subprocesses with strict timeouts (10-15 seconds) and a 4KB output truncation buffer.
- **Web Fetching (`fetch_url`)**: Strips scripts and style tags, truncating text to 8KB.
- **File System (`file_tools`)**: Safe file reading/writing scoped to your workspace.

---

## Explore Detailed Tool Manuals

- **[Code Editor & Terminal →](editor.md)** — File string replacement editor and bash tools
- **[Git & Version Control →](git.md)** — Git diff, status, log, and patch tools
- **[Web Tools →](web.md)** — Searching DuckDuckGo, reading URLs, Wikipedia summaries, HTTP REST, OpenAPI
- **[Math Tools →](math.md)** — Arithmetic, unit conversion, symbolic algebra
- **[File Tools →](files.md)** — Reading, writing, searching, and inspecting files
- **[Code Tools →](code.md)** — Running Python, shell commands, and pytest safely
- **[Date & Time Tools →](datetime.md)** — Timestamps, date arithmetic, formatting
- **[Data Tools →](data.md)** — JSON parsing, jq queries, CSV formatting, regex, SQLite queries
- **[Memory Tools →](memory.md)** — Storing and recalling session notes and persistent memory


