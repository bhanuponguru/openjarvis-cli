# OpenJarvis Built-in Tools

OpenJarvis ships with a comprehensive set of built-in tools that agents can use. These tools are organized into modules by function and can be loaded selectively.

## Quick Start

```python
from openjarvis import Conductor, create_builtin_registry

# Create registry with all tools
registry = create_builtin_registry()

# Wire into conductor
conductor = Conductor(tools=registry)

# Agent can now call any of the 49 tools
```

## Tool Modules

### `datetime_tools` — Date & Time Operations

Tools for working with dates, times, and timezones.

| Tool | Signature | Returns |
|------|-----------|---------|
| `get_current_datetime` | `(timezone: str = "UTC")` | ISO timestamp + weekday |
| `date_arithmetic` | `(date_str: str, days: int, hours: int = 0)` | ISO datetime |
| `format_datetime` | `(date_str: str, fmt: str)` | Formatted string |
| `days_between` | `(date_a: str, date_b: str)` | Integer (days) |

**Example:**
```python
registry.execute({
    "name": "date_arithmetic",
    "arguments": {"date_str": "2026-08-13", "days": 5}
})
# → "2026-08-18T00:00:00"
```

---

### `math_tools` — Calculations & Math

Safe math evaluation, unit conversion, and symbolic solving.

| Tool | Signature | Returns |
|------|-----------|---------|
| `evaluate_expression` | `(expression: str)` | Numeric result (string) |
| `convert_units` | `(value: float, from_unit: str, to_unit: str)` | Converted value (string) |
| `solve_equation` | `(equation: str, variable: str = "x")` | Solutions (string) |
| `prime_factorize` | `(n: int)` | List of prime factors |

**Supported conversions:** `m_to_km`, `km_to_m`, `ft_to_m`, `m_to_ft`, `mi_to_km`, `km_to_mi`, `kg_to_lb`, `lb_to_kg`, `c_to_f`, `f_to_c`

**Example:**
```python
# Safe evaluation (no exec, only math ops)
registry.execute({
    "name": "evaluate_expression",
    "arguments": {"expression": "2**10 + 1"}
})
# → "1025"

# Unit conversion
registry.execute({
    "name": "convert_units",
    "arguments": {"value": 5, "from_unit": "km", "to_unit": "m"}
})
# → "5000.0"
```

---

### `file_tools` — File I/O

Read, write, and search files and directories.

| Tool | Signature | Returns |
|------|-----------|---------|
| `read_file` | `(path: str, max_chars: int = 8000)` | File contents (truncated) |
| `write_file` | `(path: str, content: str, append: bool = False)` | Confirmation message |
| `list_directory` | `(path: str, pattern: str = "*")` | List of matching paths |
| `search_in_files` | `(path: str, pattern: str, glob: str = "**/*")` | List of matches with line numbers |
| `search_dir` | `(search_term: str, dir_path: str = ".")` | List of matching `{file, line, content}` |
| `search_file` | `(search_term: str, file_path: str)` | List of matching `{line, content}` |
| `find_file` | `(file_name: str, dir_path: str = ".")` | List of matching relative paths |
| `file_info` | `(path: str)` | Dict: `{size_bytes, mtime, type}` |
| `delete_file` | `(path: str)` | Confirmation message |

**Example:**
```python
# Read a file
registry.execute({
    "name": "read_file",
    "arguments": {"path": "config.yaml"}
})

# Search for pattern in files
registry.execute({
    "name": "search_in_files",
    "arguments": {"path": ".", "pattern": "TODO", "glob": "**/*.py"}
})
```

---

### `web_tools` — Web Access

Fetch URLs, search the web, execute HTTP requests, and inspect OpenAPI specs.

| Tool | Signature | Returns |
|------|-----------|---------|
| `fetch_url` | `(url: str, timeout: int = 15)` | Page text (no HTML, truncated to 8KB) |
| `search_web` | `(query: str, num_results: int = 5)` | List of `{title, url, snippet}` |
| `fetch_wikipedia` | `(topic: str, sentences: int = 5)` | Summary text |
| `http_request` | `(url: str, method: str = "GET", headers: dict = None, params: dict = None, data: str = None, json_data: dict = None, timeout: int = 15)` | Dict: `{status_code, headers, body}` |
| `parse_openapi_spec` | `(spec_text: str = None, spec_path: str = None)` | Dict with title, version, endpoints |

**Example:**
```python
# Search the web
registry.execute({
    "name": "search_web",
    "arguments": {"query": "Python async programming", "num_results": 3}
})
# → [{"title": "...", "url": "...", "snippet": "..."}]

# Get Wikipedia summary
registry.execute({
    "name": "fetch_wikipedia",
    "arguments": {"topic": "Python (programming language)"}
})
```

---

### `code_tools` — Code Execution & Linting

Execute Python and shell commands safely, and run pytest test suites.

| Tool | Signature | Returns |
|------|-----------|---------|
| `run_python` | `(code: str, timeout: int = 10)` | stdout + stderr (4KB cap) |
| `run_shell` | `(command: str, timeout: int = 15)` | stdout + stderr (4KB cap) |
| `lint_python` | `(code: str)` | "Syntax OK" or error message |
| `run_pytest` | `(test_path: str = "", args: str = "")` | Test execution counts and output |

**Safety:** Subprocess-based with timeout; output capped at 4KB. Inherits environment but no special network access.

**Example:**
```python
# Execute Python
registry.execute({
    "name": "run_python",
    "arguments": {"code": "import json; print(json.dumps({'key': 'value'}))"}
})

# Run shell command
registry.execute({
    "name": "run_shell",
    "arguments": {"command": "ls -la | grep .py"}
})

# Check syntax without running
registry.execute({
    "name": "lint_python",
    "arguments": {"code": "x = 1\ny = 2 +"}  # missing operand
})
```

---

### `data_tools` — Data Parsing & Transformation

Parse JSON, CSV, query SQLite databases, and apply regex operations.

| Tool | Signature | Returns |
|------|-----------|---------|
| `parse_json` | `(json_str: str)` | Pretty-printed JSON |
| `jq_query` | `(json_str: str, path: str)` | Query result (dot-notation paths) |
| `parse_csv` | `(csv_str: str, delimiter: str = ",")` | Markdown table (first 20 rows) |
| `regex_search` | `(pattern: str, text: str)` | List of matches |
| `regex_replace` | `(pattern: str, replacement: str, text: str)` | Modified text |
| `sql_query` | `(query: str, db_path: str = ":memory:")` | Formatted Markdown table or status |

**Example:**
```python
# Parse JSON
registry.execute({
    "name": "parse_json",
    "arguments": {"json_str": '{"users": [{"name": "Alice"}]}'}
})

# Query JSON with dot notation
registry.execute({
    "name": "jq_query",
    "arguments": {"json_str": '{"users": [{"name": "Alice"}]}', "path": "users.0.name"}
})
# → "Alice"

# Regex operations
registry.execute({
    "name": "regex_search",
    "arguments": {"pattern": r"\d+", "text": "abc123def456"}
})
# → ["123", "456"]
```

---

### `memory_tools` — Session & Persistent Memory

Store and retrieve notes and persistent memory during and across sessions.

| Tool | Signature | Returns |
|------|-----------|---------|
| `save_memory` | `(name: str, content: str, scope: str = "local")` | Confirmation message |
| `read_memory` | `(name: str, scope: str = "local")` | Markdown content |
| `update_memory` | `(name: str, content: str, scope: str = "local")` | Confirmation message |
| `delete_memory` | `(name: str, scope: str = "local")` | Confirmation message |
| `list_memories` | `(scope: str = "local")` | List of memory names |
| `search_memories` | `(query: str, scope: str = "all")` | List of `{name, scope, snippet}` |
| `store_note` | `(key: str, content: str)` | Confirmation (local alias) |
| `recall_note` | `(key: str)` | Note content (local alias) |
| `list_notes` | `()` | List of keys (local alias) |
| `delete_note` | `(key: str)` | Confirmation (local alias) |

**Example:**
```python
# Save memory in local project scope
registry.execute({
    "name": "save_memory",
    "arguments": {"name": "project_goals", "content": "- Benchmark support\n- Codebase audit", "scope": "local"}
})

# Search memories across all scopes
registry.execute({
    "name": "search_memories",
    "arguments": {"query": "Benchmark"}
})
```

---

### `editor_tools` — Code Editor & Terminal Execution

File editing and shell execution with atomic string replacements, undo history, and bash execution.

| Tool | Signature | Returns |
|------|-----------|---------|
| `str_replace_editor` | `(command: str, path: str, file_text: str = None, old_str: str = None, new_str: str = None, insert_line: int = None, view_range: list[int] = None)` | Status or file content |
| `execute_bash` | `(command: str, timeout_seconds: int = 30, cwd: str = None)` | Exit code, stdout, stderr |
| `bash` | `(command: str, timeout_seconds: int = 30, cwd: str = None)` | Standard bash execution alias |

**Supported `str_replace_editor` commands:**
- `view`: Display numbered lines (supports optional `view_range=[start, end]`).
- `create`: Create a new file with `file_text`.
- `str_replace`: Replace unique `old_str` with `new_str` (or empty string if omitted for deletion).
- `insert`: Insert `new_str` after `insert_line` (or at file beginning if `insert_line=0`).
- `undo_edit`: Revert last modification made to `path`.

---

### `git_tools` — Git & Version Control

Inspect differences, view status and commit history, and apply unified diff patches.

| Tool | Signature | Returns |
|------|-----------|---------|
| `git_diff` | `(path: str = "", cached: bool = False)` | Unified git diff string |
| `git_status` | `()` | Working tree status summary |
| `git_log` | `(max_count: int = 5)` | Recent commit log summary |
| `apply_patch` | `(patch: str)` | Patch application confirmation |

---

## Selective Loading

Load only specific tools:

```python
# Only datetime, math, and git tools
registry = create_builtin_registry(include={"datetime_tools", "math_tools", "git_tools"})

# All except code execution (safer for untrusted agents)
registry = create_builtin_registry(exclude={"code_tools", "editor_tools"})

# Fine-grained control
registry = create_builtin_registry(
    include={"datetime_tools", "math_tools", "file_tools", "git_tools"},
    exclude={"code_tools"}
)
```

---

## Dependencies

### Required
- `httpx >= 0.25` — for web fetching
- `duckduckgo-search >= 6.0` — for web search
- `pytz >= 2024.1` — for timezone handling

### Optional (Lazy)
- `sympy >= 1.12` — imported only when `solve_equation` is called; graceful error if missing

---

## Safety Considerations

- **`evaluate_expression`**: Uses AST validation — only arithmetic operators, no `exec` or `eval`.
- **`run_python` / `run_shell`**: Subprocess-based; output truncated to 4KB; inherits env but no special capabilities.
- **`write_file` / `delete_file`**: Work relative to current working directory; no path traversal guards beyond OS.
- **`fetch_url`**: Strips `<script>` and `<style>` tags; truncates to 8KB.
- **`search_in_files`**: Limited to 100 matches across all files to prevent memory exhaustion.

---

## Integration with Conductor

Tools are automatically called by the `Conductor` when the LLM emits tool calls:

```python
from openjarvis import Conductor, create_builtin_registry

registry = create_builtin_registry()
conductor = Conductor(config_path="specialists.yaml", tools=registry)

# In the agent loop, the conductor will:
# 1. Send tool schema to the LLM
# 2. Parse tool calls from LLM response
# 3. Execute via registry.execute()
# 4. Feed results back to LLM for next turn

for event in conductor.chat("What is the weather in Paris?"):
    if event["type"] == "final":
        print(event["content"])
```

---

## Testing Tools

All tools have comprehensive test coverage. Run tests:

```bash
uv run python -m pytest tests/test_builtin_tools.py -v
```
