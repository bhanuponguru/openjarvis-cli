# Command Line Interface

OpenJarvis runs as an interactive terminal application.

---

## Starting OpenJarvis

```bash
openjarvis
```

Both `openjarvis` and the short alias `oj` work:

```bash
oj
```

On startup, OpenJarvis loads your configuration and prints a ready prompt:

```
OpenJarvis — type exit or quit to stop

>
```

---

## Interactive Session

Type your query at the `>` prompt and press Enter:

```
> What is the capital of France?

Paris is the capital of France.

> Calculate compound interest on $10,000 at 5% for 10 years

  ↳ routing: generalist → math → tool_use
  ⚙ tool: evaluate_expression
    → 16288.94...
  ↳ routing: tool_use → math → generalist

$10,000 at 5% compound interest for 10 years grows to approximately $16,288.95.
```

### Multi-line Input

For long queries, type everything on one line. OpenJarvis does not support multi-line input at the prompt — paste code or long text as a single line or use a file:

```
> Read the file my_code.py and explain what it does
```

### Exiting

Type `exit` or `quit` to stop:

```
> exit
```

Or press `Ctrl+C` or `Ctrl+D` to exit immediately.

---

## Configuration

OpenJarvis finds your configuration automatically. No flags needed for the common case:

```bash
openjarvis        # Uses specialists.yaml in current directory (or ~/.config/openjarvis/)
```

### Using a Specific Config File

```bash
openjarvis --config /path/to/my-config.yaml
```

Or set it permanently via environment variable:

```bash
export OJ_CONFIG=/path/to/my-config.yaml
openjarvis
```

### Config Search Order

1. `--config` flag
2. `OJ_CONFIG` environment variable
3. `specialists.yaml` in current directory
4. `~/.config/openjarvis/specialists.yaml`

---

## Output Format

### Routing Indicators

When a request is routed through specialists, you see the path in dim text:

```
  ↳ routing: generalist → code
  ↳ routing: code → math
  ↳ routing: math → tool_use
  ↳ routing: tool_use → math
  ↳ routing: math → code
  ↳ routing: code → generalist
```

### Tool Execution

When a specialist invokes a tool:

```
  ⚙ tool: search_web
    → [{"title": "...", "url": "...", "snippet": "..."}]
```

The `⚙ tool:` line shows the tool name. The `→` line shows a preview of the result (truncated to 120 characters).

### Final Response

The final answer is rendered as Markdown — headers, bold text, code blocks, and lists display formatted in the terminal.

### Errors

Errors appear in red:

```
  ⚠ Connection refused: check that Ollama is running at http://localhost:11434
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit query |
| `Ctrl+C` | Exit (or cancel current input) |
| `Ctrl+D` | Exit |
| `↑` / `↓` | Navigate command history (if supported by your terminal) |

---

## Tips

**Running from your project directory:**
Place `specialists.yaml` in your project root and run `openjarvis` from there. It picks up the config automatically.

**Switching configs quickly:**
```bash
OJ_CONFIG=~/configs/research.yaml openjarvis
```

**Quiet sessions:**
Simple questions that don't need routing produce no routing output — just the answer.

**Long responses:**
Responses are rendered with Markdown formatting. Code blocks are syntax-highlighted.

---

## See Also

- [Quick Start](../getting-started/quick-start.md) — First-time setup
- [Configuration Overview](../configuration/overview.md) — Config file reference
- [Routing Protocol](routing.md) — How routing works
- [Troubleshooting](../troubleshooting.md) — Common issues
