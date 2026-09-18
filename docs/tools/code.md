# Code Execution Tools

OpenJarvis includes 4 code tools for running Python, executing shell commands, checking Python syntax, and running pytest test suites.

---

## Tools

### `run_python`

Execute Python code in a subprocess and return its output.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | string | required | Python code to execute |
| `timeout` | integer | 10 | Timeout in seconds |

**Returns:** Combined stdout and stderr output (capped at 4KB).

**Example prompts:**
```
> Run this Python code and show me the output: print([x**2 for x in range(10)])
> Execute: import json; print(json.dumps({"key": "value"}, indent=2))
> Calculate the Fibonacci sequence up to 100 using Python
```

---

### `run_shell`

Execute a shell command and return its output.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `command` | string | required | Shell command to execute |
| `timeout` | integer | 15 | Timeout in seconds |

**Returns:** Combined stdout and stderr output (capped at 4KB).

**Example prompts:**
```
> Run: ls -la | grep .py
> Execute: git log --oneline -10
> Check the disk space: df -h
```

---

### `lint_python`

Check Python code for syntax errors without executing it.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | yes | Python code to check |

**Returns:** `"Syntax OK"` or an error message with line number.

**Example prompts:**
```
> Check if this Python code has any syntax errors: [paste code]
> Validate this Python snippet before running it
```

---

### `run_pytest`

Run pytest on a test suite or specific test file and return execution output with pass/fail counts.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `test_path` | string | `""` | Optional path to specific test file or directory |
| `args` | string | `""` | Optional additional pytest arguments (e.g. `"-k test_editor -v"`) |

**Returns:** Output string including exit code, test pass/fail counts, and failure tracebacks.

---

## Usage Examples

### Running Python Subprocesses

```text
oj> Calculate the sum of squares from 1 to 100 using Python

  ↳ routing: generalist → code
  ⚙ tool: run_python {"code": "print(sum(i**2 for i in range(1, 101)))"}
    → 338350

The sum of squares from 1 to 100 is **338,350**.
```

### Checking Generated Python Code

```text
oj> Check if this Python function has any syntax issues: def foo(x): return x + 1

  ↳ routing: generalist → code
  ⚙ tool: lint_python {"code": "def foo(x):\n    return x + 1"}
    → "Syntax OK"

The snippet contains valid Python syntax without errors.
```

---

## Security & Timeout Guardrails

Code execution tools run directly in isolated subprocesses using the active user's permissions:

- **Subprocess Isolation**: Subprocesses are spawned per-execution without shell string injection.
- **Strict Timeouts**: 10 seconds for `run_python`, 15 seconds for `run_shell`.
- **Buffer Cap**: Standard output and error streams are truncated to 4KB.
- **Static Linting (`lint_python`)**: Uses Python's internal AST parser to validate syntax safely without executing code.

---

## See Also

- [Tools Overview](overview.md) — All 49 built-in tools
- [File Tools](files.md) — Reading, writing, and searching files
- [Data Processing](data.md) — JSON, CSV, and regex operations
