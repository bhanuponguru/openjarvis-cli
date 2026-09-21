# Security, Permissions & Guardrails

OpenJarvis CLI implements an execution permission manager to ensure that autonomous tool invocations (terminal commands, file writes, code execution) adhere to configured safety policies.

---

## 1. Operating Modes

The permission manager intercepts tool invocations prior to dispatch and evaluates them against the configured mode:

| Mode | Evaluation Logic | Default Action |
| :--- | :--- | :--- |
| **`interactive`** (Default) | Evaluates blocklists, remembered decisions, and rules. If unapproved, prompts the user interactively in the terminal for confirmation. | Prompt for user confirmation. |
| **`autonomous`** | Executes allowed tools automatically. If a safety classifier is loaded, evaluates risky commands before execution. Blocklists and deny rules take precedence. | Auto-allow execution. |
| **`allowlist`** | Only tools explicitly enumerated in `allowed_tools` execute without confirmation. All unlisted tools trigger confirmation prompts. | Prompt if not explicitly allowlisted. |

```bash
# Launch with autonomous execution (equivalent to -y / --auto-approve)
openjarvis --mode autonomous

# Launch with interactive confirmation prompts
openjarvis --mode interactive

# Headless / CI execution with auto-approval
openjarvis -y -p "Run pytest and lint checks"
```

---

## 2. Configuration Schema

Permission policies are defined under the `tool_permissions` block in `.openjarvis/config.yaml`:

```yaml
# .openjarvis/config.yaml
tool_permissions:
  mode: "interactive"  # interactive | autonomous | allowlist

  # Tools permitted to execute without prompts in allowlist mode
  allowed_tools:
    - read_file
    - search_dir
    - search_in_files
    - find_file
    - git_status
    - git_diff

  # Tools explicitly forbidden from executing
  blocked_tools:
    - delete_file

  # Granular argument-level pattern rules (evaluated via fnmatch)
  rules:
    bash:
      argument_patterns:
        - match:
            command: "git status*"
          action: "allow"
        - match:
            command: "pytest*"
          action: "allow"
        - match:
            command: "rm -rf*"
          action: "deny"
      default_action: "confirm"

    str_replace_editor:
      argument_patterns:
        - match:
            path: "src/*"
          action: "allow"
        - match:
            path: "tests/*"
          action: "allow"
      default_action: "confirm"
```

---

## 3. Evaluation Precedence

When a tool invocation is intercepted, `PermissionManager.check()` evaluates the request in the following order:

1. **Global Blocklist**: If `tool_name` is in `blocked_tools`, the execution is immediately denied (`action="deny"`).
2. **Remembered Decisions**: If the user previously selected "Always Allow" or "Always Block" in interactive mode, the persisted decision from `permissions.yaml` is applied.
3. **MAS Meta-Tools**: Internal multi-agent coordination tools (`spawn_agent`, `connect_agents`, `report_findings`, `exit_agent`, `complete_task`) are engine coordination primitives and are unconditionally allowed (`action="allow"`).
4. **Argument Pattern Rules**: If the tool has entry in `rules`, `argument_patterns` are evaluated sequentially using `fnmatch`. The first matching pattern returns its specified action (`allow`, `deny`, or `confirm`). If none match, `default_action` applies.
5. **Global Allowlist**: If `tool_name` is in `allowed_tools`, execution is allowed.
6. **Safety Classifier (Autonomous Mode)**: If running in `autonomous` mode and a safety classifier model is active, the classifier evaluates the tool name, arguments, and user intent.
7. **Mode Default Fallback**:
   - `autonomous`: Allows execution.
   - `allowlist`: Returns `confirm` (not in allowlist).
   - `interactive`: Returns `confirm`.

---

## 4. Persisted Permissions

Interactive decisions can be saved across sessions. When a user confirms or denies a tool in the terminal, the decision can be persisted to:

- Workspace scope: `.openjarvis/config/permissions.yaml`
- Global scope: `~/.openjarvis/config/permissions.yaml`

```yaml
# .openjarvis/config/permissions.yaml
mode: interactive
allowed_tools:
  - read_file
  - search_in_files
blocked_tools:
  - delete_file
remembered_decisions:
  run_pytest: allow
  execute_bash: confirm
```

---

## 5. Subprocess Boundaries & Timeouts

Tools that invoke local subprocesses (`bash`, `run_shell`, `run_python`, `run_pytest`) enforce subprocess timeouts (default: 30 seconds) to prevent hung processes, unhandled loops, and unresponsive commands. Non-zero exit codes and standard error streams are returned directly into the agent context for error handling.
