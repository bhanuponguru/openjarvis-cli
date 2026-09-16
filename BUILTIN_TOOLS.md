# OpenJarvis Built-in Tools

OpenJarvis ships with a comprehensive set of built-in tools that agents can use. These tools are organized into modules by function and can be loaded selectively.

## Quick Start

```python
from openjarvis import Conductor, create_builtin_registry

# Create registry with all tools
registry = create_builtin_registry()

# Wire into conductor
conductor = Conductor(tools=registry)

# Agent can now call any of the 29 tools
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

Fetch URLs, search the web, and fetch Wikipedia summaries.

| Tool | Signature | Returns |
|------|-----------|---------|
| `fetch_url` | `(url: str, timeout: int = 15)` | Page text (no HTML, truncated to 8KB) |
| `search_web` | `(query: str, num_results: int = 5)` | List of `{title, url, snippet}` |
| `fetch_wikipedia` | `(topic: str, sentences: int = 5)` | Summary text |

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

Execute Python and shell commands safely, with timeouts.

| Tool | Signature | Returns |
|------|-----------|---------|
| `run_python` | `(code: str, timeout: int = 10)` | stdout + stderr (4KB cap) |
| `run_shell` | `(command: str, timeout: int = 15)` | stdout + stderr (4KB cap) |
| `lint_python` | `(code: str)` | "Syntax OK" or error message |

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

Parse JSON, CSV, and apply regex operations.

| Tool | Signature | Returns |
|------|-----------|---------|
| `parse_json` | `(json_str: str)` | Pretty-printed JSON |
| `jq_query` | `(json_str: str, path: str)` | Query result (dot-notation paths) |
| `parse_csv` | `(csv_str: str, delimiter: str = ",")` | Markdown table (first 20 rows) |
| `regex_search` | `(pattern: str, text: str)` | List of matches |
| `regex_replace` | `(pattern: str, replacement: str, text: str)` | Modified text |

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

### `memory_tools` — Session Memory

Store and retrieve notes during a session.

| Tool | Signature | Returns |
|------|-----------|---------|
| `store_note` | `(key: str, content: str)` | Confirmation |
| `recall_note` | `(key: str)` | Note content or error |
| `list_notes` | `()` | List of keys |
| `delete_note` | `(key: str)` | Confirmation or error |

**Example:**
```python
# Store context
registry.execute({
    "name": "store_note",
    "arguments": {"key": "user_preferences", "content": "dark mode, sans-serif"}
})

# Recall later
registry.execute({
    "name": "recall_note",
    "arguments": {"key": "user_preferences"}
})
# → "dark mode, sans-serif"
```

---

## Selective Loading

Load only specific tools:

```python
# Only datetime and math tools
registry = create_builtin_registry(include={"datetime_tools", "math_tools"})

# All except code execution (safer for untrusted agents)
registry = create_builtin_registry(exclude={"code_tools"})

# Fine-grained control
registry = create_builtin_registry(
    include={"datetime_tools", "math_tools", "file_tools"},
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
