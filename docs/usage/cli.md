# Command Line Interface

OpenJarvis operates as a terminal application with an interactive REPL, rich formatting, multi-agent event tracing, and non-interactive batch execution.

---

## 1. Invocation

Launch OpenJarvis using either the standard binary name or short alias:

```bash
openjarvis
# Or using the short alias:
oj
```

---

## 2. CLI Options & Flags

```text
Usage: openjarvis [-h] [-c CONFIG] [-v] [--model MODEL] [--provider PROVIDER]
                  [--update-tools] [-y] [--mode {interactive,autonomous,allowlist}]
                  [-V] [query ...]

Autonomous dynamic Multi-Agent System (MAS) coordinating specialized Conductor agents

Positional Arguments:
  query                 Optional non-interactive query or instruction to execute

Options:
  -c, --config CONFIG   Path to config.yaml configuration file
  -v, --verbose         Display live inter-agent messaging, spawning, and tool events
  --model MODEL         Override root agent model name
  --provider PROVIDER   Override default provider (e.g. ollama, openai, anthropic)
  --update-tools        Re-index and update tool embedding vectors
  -y, --auto-approve    Automatically approve tool executions without prompting
  --mode {interactive,autonomous,allowlist}
                        Tool permission enforcement mode
  -V, --version         Show program's version number and exit
  -h, --help            Show this help message and exit
```

---

## 3. Execution Modes

### Interactive REPL Mode
Invoking `openjarvis` without positional arguments launches the interactive terminal prompt:

```bash
openjarvis
```

Prompt controls:
- Submit: `Enter`
- Multiline newline: `Escape` followed by `Enter` (or `Alt+Enter`)
- History navigation: `Up` / `Down` arrows
- Exit: `/exit`, `/quit`, `exit`, `quit`, or `Ctrl+D`

### Non-Interactive (Single-Shot) Execution
Pass the task string as positional arguments:

```bash
oj "Inspect pyproject.toml and summarize installed package dependencies"
```

### Unattended / Headless Execution (`-y` / `--auto-approve`)
For scripts, CI/CD runners, and non-interactive automation where stdin cannot receive confirmation prompts, specify `-y` or `--auto-approve` (which sets permission mode to `autonomous`):

```bash
oj -y "Run pytest and generate summary report"
```

### Real-Time Event Tracing (`-v` / `--verbose`)
By default, OpenJarvis displays a status spinner during agent coordination and renders final responses and error events.
Passing `-v` enables streaming log events for:
- Agent spawning (`spawn_agent`)
- Graph topology edges (`connect_agents`)
- Tool execution parameters and outputs
- Intermediate findings reports (`report_findings`)
- Agent exit notifications (`exit_agent`)
- Deliverable artifact saves

```bash
oj -v "Analyze git log and identify the last 5 merged features"
```

---

## 4. Configuration Overrides

Override configuration parameters per command invocation:

```bash
# Explicit configuration path:
oj -c ~/.openjarvis/coding.yaml

# Override model and provider:
oj --provider openai --model gpt-4o "Refactor src/parser.py"

# Enforce strict allowlist permissions:
oj --mode allowlist "Review codebase"
```

---

## 5. Built-in REPL Commands

Within the interactive terminal, slash commands provide utility functions:

| Command | Action |
| :--- | :--- |
| `/help` | Display list of interactive commands and navigation shortcuts |
| `/version` | Display active version identifier |
| `/clear` | Clear terminal scrollback buffer |
| `/update-tools` | Re-index vector embeddings for Two-Phase Tool Retrieval |
| `/exit`, `/quit` | Terminate session |

---

## 6. Generated Artifact Storage

Deliverables produced by agents calling `exit_agent` or `complete_task` are persisted to disk via the content-addressable `ArtifactStore`:

```text
.openjarvis/artifacts/
├── art-6c2e391b_researcher_output.md
└── art-b94f18da_final_output.md
```

The CLI prints clickable file paths upon task conclusion.
