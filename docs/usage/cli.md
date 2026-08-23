# Command Line Interface

OpenJarvis runs as a terminal application with an interactive REPL, rich syntax highlighting, and multi-line editing.

---

## Starting OpenJarvis

Launch OpenJarvis from your terminal:

```bash
openjarvis
```

You can also use the short binary alias if available:

```bash
oj
```

On launch, OpenJarvis discovers your configuration and opens the interactive prompt:

```text
OpenJarvis (type 'exit' or 'quit' to stop)

oj> 
```

---

## Interactive REPL

Type your question or instruction at the `oj>` prompt and press `Enter`:

```text
oj> Calculate compound interest on $10,000 at 5% for 10 years

  ↳ routing: generalist → math
  ⚙ tool: evaluate_expression {"expression": "10000 * (1 + 0.05)**10"}
    → 16288.946...

$10,000 at 5% annual compound interest for 10 years grows to approximately **$16,288.95**.
```

### Multi-Line Input
To enter multi-line text (e.g. multi-line code snippets or long prompts):
- Press `Escape` followed by `Enter` (or `Alt+Enter`) to insert a new line without submitting.
- Press `Enter` on its own when ready to submit.

### Command History
- Press `↑` (Up Arrow) and `↓` (Down Arrow) to browse through your previous prompts.
- History is saved automatically to `~/.config/openjarvis/history`.

### Exiting the Session
- Type `exit` or `quit` and press `Enter`.
- Or press `Ctrl+D` (EOF) or `Ctrl+C`.

---

## Configuration Discovery

OpenJarvis searches for your configuration in the following order:

1. **`OJ_CONFIG` environment variable**:
   ```bash
   OJ_CONFIG=/path/to/custom-config.yaml openjarvis
   ```
2. **Current working directory**: `./specialists.yaml`
3. **User configuration directory**: `~/.config/openjarvis/specialists.yaml`
4. **System-wide directory**: `/etc/openjarvis/specialists.yaml` (Linux / macOS)

If no configuration exists, OpenJarvis launches the **first-run setup wizard** to help you configure your preferred provider.

---

## Visual Feedback

### Routing Path
When OpenJarvis routes between specialists, it prints each hop in dim text:

```text
  ↳ routing: generalist → code
  ↳ routing: code → math
```

### Function & Tool Invocations
When a specialist calls a built-in tool, OpenJarvis displays the tool name, arguments, and return preview:

```text
  ⚙ tool: search_web {"query": "OpenAI API"}
    → [{"title": "Overview - OpenAI API", ...}]
```

### Formatted Markdown
Final synthesized responses are rendered with rich Markdown formatting in your terminal, including bold text, bullet lists, tables, and syntax-highlighted code blocks.

---

## Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `Enter` | Submit query |
| `Escape` then `Enter` | Insert newline (multi-line input) |
| `↑` / `↓` | Navigate command history |
| `Ctrl+C` | Cancel current prompt / Exit |
| `Ctrl+D` | Exit OpenJarvis session |

---

## See Also

- [Quick Start Guide](../getting-started/quick-start.md) — First-time setup
- [Configuration Overview](../configuration/overview.md) — Config file structure
- [Routing Protocol](routing.md) — How routing tags work
- [Troubleshooting](../troubleshooting.md) — Common error resolution
