# System Tools

Dedicated system tools (environment variable access, system information) are planned for a future release.

In the meantime, specialists can gather system information using the **Code Execution** tools.

---

## Getting System Information Now

### Environment Variables

Use `run_shell` to read environment variables:

```
> What is my HOME directory?

  ↳ routing: generalist → tool_use
  ⚙ tool: run_shell
    → /home/alice
  ↳ routing: tool_use → generalist

Your HOME directory is /home/alice.
```

Common environment variable queries:
```
> What is the value of the PATH environment variable?
> What shell am I using? (check SHELL)
> What is my username? (check USER or USERNAME)
```

### System Information

Use `run_shell` for system details:

```
> What operating system am I running?

  ↳ routing: generalist → code → tool_use
  ⚙ tool: run_shell
    → Linux 6.1.0 x86_64
  ↳ routing: tool_use → code → generalist
```

Example queries:
```
> How much free disk space do I have?
> How much RAM does my system have?
> What is my system's hostname?
> Show me running processes
```

### Python-Based System Info

Use `run_python` for cross-platform system information:

```
> Show me my system's basic information

  ↳ routing: generalist → code → tool_use
  ⚙ tool: run_python
    → System: Linux
    → Node: mycomputer
    → Python: 3.12.0
  ↳ routing: tool_use → code → generalist
```

---

## Coming in a Future Release

Planned dedicated system tools:

| Tool | Description |
|------|-------------|
| `get_env_var` | Read a specific environment variable safely |
| `get_system_info` | Get OS, CPU, memory, and disk information |

These will provide system access without requiring shell command execution.

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [Code Execution](code.md) — Run Python and shell commands
- [File Tools](files.md) — File system access
