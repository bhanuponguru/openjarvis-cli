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

---

## Command-Line Arguments & Options

OpenJarvis supports both interactive and non-interactive command-line invocation:

```text
Usage: openjarvis [-h] [-c CONFIG] [--model MODEL] [--provider PROVIDER]
                  [--update-tools] [-V] [query ...]

Options:
  -c, --config CONFIG  Path to specialists.yaml configuration file
  --model MODEL        Override generalist model name
  --provider PROVIDER  Override default provider (e.g. ollama, openai, anthropic)
  --update-tools       Re-index and update tool embedding vectors
  -V, --version        Show program's version number and exit
  -h, --help           Show this help message and exit
```

### Non-Interactive Single Prompt

To execute a one-off instruction without entering the interactive prompt:

```bash
oj "List the largest files in the current directory"
```

### Overriding Configuration on the Fly

```bash
# Use a specific configuration file:
oj -c /path/to/custom-specialists.yaml

# Override the generalist provider and model:
oj --provider openai --model gpt-4o
```

---

## Interactive REPL

On launch without arguments, OpenJarvis discovers your configuration and opens the interactive prompt:

```text
OpenJarvis v{{ version }} — type /exit to stop, /help for commands

oj> 
```

### REPL Commands

| Command | Shortcut | Description |
| :--- | :--- | :--- |
| `/help` | | Show available REPL commands and shortcuts |
| `/version` | `/v` | Print the current `openjarvis-cli` version |
| `/clear` | | Clear the terminal screen |
| `/update-tools` | | Re-compute and cache tool embedding vectors |
| `/exit`, `/quit` | `exit`, `quit` | End the session |

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
