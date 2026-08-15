# Code Execution Tools

OpenJarvis includes 3 code tools for running Python, executing shell commands, and checking Python syntax.

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

## Usage Examples

### Running a Calculation

```
> Calculate the sum of squares from 1 to 100 using Python

  ↳ routing: generalist → code → tool_use
  ⚙ tool: run_python
    → 338350
  ↳ routing: tool_use → code → generalist

The sum of squares from 1 to 100 is 338,350.
(Calculated with: sum(i**2 for i in range(1, 101)))
```

### Checking Generated Code

```
> Write and test a Python function to check if a number is prime

  ↳ routing: generalist → code → tool_use
  ⚙ tool: lint_python
    → Syntax OK
  ⚙ tool: run_python
    → True
    → False
    → True
  ↳ routing: tool_use → code → generalist

Here's a prime-checking function: [code shown]
```

---

## Security Warning

Code execution tools run directly on your machine with your user's permissions. This means:

- Python code can read/write any file you have access to
- Shell commands can do anything your user can do
- Network access is available
- System resources can be consumed or exhausted
- **There is no sandbox**

**Only use with trusted inputs.** If you're asking OpenJarvis to execute code from untrusted sources (web pages, user input, etc.), review the code before it runs.

### Timeout Protection

Both tools enforce timeouts (10s for Python, 15s for shell) to prevent runaway processes. Output is capped at 4KB to prevent memory issues.

---

## Tool Access Requirements

Code tools require the `tool_use` specialist, which in turn requires `delegates_to` to be set:

```yaml
specialists:
  code:
    delegates_to: ["tool_use"]   # Required

  tool_use:
    system_prompt: |
      You are a tool specialist. Execute tools carefully.
      End with [RETURN].
    base_url: "..."
    model: "..."
```

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [File Tools](files.md) — Read and write files
- [Troubleshooting](../troubleshooting.md) — Code execution issues
