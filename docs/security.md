# Security, Sandboxing & Permissions

OpenJarvis CLI implements an execution permission manager to ensure that autonomous tool executions (terminal bash commands, file modifications, code evaluation) remain safe and user-controlled.

---

## 1. Permission Approval Modes

The permission manager intercepts every tool invocation before execution and supports three operating modes:

| Mode | Behavior | Best Used For |
| :--- | :--- | :--- |
| **`prompt`** (Default) | Interactively asks the user to approve each tool call before execution. | General daily interactive terminal usage. |
| **`auto_allow`** | Automatically approves matching tools without prompting. | Headless CI/CD automation or trusted local scripts. |
| **`deny_all`** | Rejects all tool executions; models can only respond with text. | Strict read-only inspection or untrusted environments. |

---

## 2. Granular Rules & Path Constraints

Permissions can be configured per-tool with exact argument constraints:

```yaml
permissions:
  mode: "prompt"
  allow_patterns:
    - tool: "str_replace_editor"
      arg_pattern: "^(src|tests)/"  # Only allow edits within src and tests
    - tool: "execute_bash"
      arg_pattern: "^(git status|pytest|ruff)" # Allow safe dev commands
  deny_patterns:
    - tool: "execute_bash"
      arg_pattern: "(rm -rf|mkfs|sudo)" # Block catastrophic commands
```

---

## 3. Subprocess Isolation & Timeouts

Tools that execute shell or subprocess commands (e.g. `execute_bash`, `run_python`) enforce strict timeouts (default: 30 seconds) to prevent infinite loops, hanging commands, or rogue subprocesses.
