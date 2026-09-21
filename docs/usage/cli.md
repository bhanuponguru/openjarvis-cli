# Command Line Interface

OpenJarvis runs as a terminal application with an interactive REPL, rich syntax highlighting, multi-agent coordination, and live progress indicators.

---

## Starting OpenJarvis

Launch OpenJarvis from your terminal:

```bash
openjarvis
```

You can also use the short binary alias:

```bash
oj
```

---

## Command-Line Arguments & Options

OpenJarvis supports both interactive and non-interactive command-line invocation:

```text
Usage: openjarvis [-h] [-c CONFIG] [-v] [--model MODEL] [--provider PROVIDER]
                  [--update-tools] [-V] [query ...]

Options:
  -c, --config CONFIG  Path to config.yaml configuration file
  -v, --verbose        Display live inter-agent messaging, spawning, and tool events
  --model MODEL        Override root agent model name
  --provider PROVIDER  Override default provider (e.g. ollama, openai, anthropic)
  --update-tools       Re-index and update tool embedding vectors
  -V, --version        Show program's version number and exit
  -h, --help           Show this help message and exit
```

### Non-Interactive Single Prompt

To execute a one-off instruction without entering the interactive prompt:

```bash
oj "Analyze the repository and summarize key architectural components"
```

### Verbose Mode (`-v` / `--verbose`)

By default, OpenJarvis displays a clean spinner while child agents coordinate in the background, printing only the final response and generated artifacts.

To inspect the real-time multi-agent graph lifecycle (spawning, neighbor consensus, and tool calls), pass the `-v` or `--verbose` flag:

```bash
oj -v "Research and implement a caching layer for database queries"
```

### Overriding Configuration on the Fly

```bash
# Use a specific configuration file:
oj -c /path/to/custom-config.yaml

# Override the root agent provider and model:
oj --provider openai --model gpt-4o
```

---

## Interactive REPL

On launch without arguments, OpenJarvis opens the interactive prompt:

```text
OpenJarvis Multi-Agent System v{{ version }} — type /exit to stop, /help for commands

oj> 
```

### REPL Commands

| Command | Description |
| :--- | :--- |
| `/help` | Show available REPL commands and shortcuts |
| `/version` | Print the current `openjarvis-cli` version |
| `/clear` | Clear the terminal screen |
| `/update-tools` | Re-compute and cache tool embedding vectors |
| `/exit`, `/quit` | End the session |

---

## Artifact Deliverables

Artifacts produced by child agents upon exit are automatically saved under your project's `.openjarvis/artifacts/` directory:

```text
.openjarvis/artifacts/
├── art-8a12bc4f_researcher_output.md
└── art-f9c312da_coder_patch.py
```

When execution concludes, OpenJarvis prints a summary of all generated artifacts with clickable local paths.
