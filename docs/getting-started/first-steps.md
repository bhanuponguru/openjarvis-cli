# First Steps

This guide demonstrates basic interaction patterns, multi-agent coordination, and tool execution in OpenJarvis CLI.

---

## Interactive REPL

Start an interactive terminal session:

```bash
openjarvis
```

The interactive prompt accepts multi-turn queries, tasks, and slash directives:

```text
OpenJarvis (type 'exit' or 'quit' to stop)

oj> 
```

Submit a prompt by pressing `Enter`. To insert a newline without submitting, press `Escape` followed by `Enter` (or `Alt+Enter`).

---

## Example Execution Traces

### 1. Arithmetic & Symbolic Computation

```text
oj> Solve for x: 3*x + 15 = 45 and factorize the result

  [root] ⚙ spawn_agent {"role": "math", "task": "Solve 3*x + 15 = 45 and factorize x"}
    → Agent 'agent-math' spawned
  [agent-math] ⚙ solve_equation {"equation": "3*x + 15 = 45", "variable": "x"}
    → "[10]"
  [agent-math] ⚙ prime_factorize {"n": 10}
    → "[2, 5]"
  [agent-math] ⚙ report_findings {"recipient": "root", "findings": "x = 10, prime factors: [2, 5]"}
    → Findings delivered to 'root'
  [agent-math] ⚙ exit_agent {"status": "success"}
    → Agent 'agent-math' terminated
  [root] ⚙ complete_task {"summary": "Solved equation: x = 10, prime factorization: 2 * 5"}

For the equation `3x + 15 = 45`:
- **x = 10**
- Prime factorization: **2 × 5**
```

### 2. Live Web Search & Extraction

```text
oj> Search for Python 3.14 release schedule

  [root] ⚙ spawn_agent {"role": "researcher", "task": "Find Python 3.14 release schedule details"}
    → Agent 'agent-researcher' spawned
  [agent-researcher] ⚙ search_web {"query": "Python 3.14 release schedule PEP 745"}
    → [{"title": "PEP 745 – Python 3.14 Release Schedule", "url": "https://peps.python.org/pep-0745/", ...}]
  [agent-researcher] ⚙ fetch_url {"url": "https://peps.python.org/pep-0745/"}
    → "..."
  [agent-researcher] ⚙ report_findings {"recipient": "root", "findings": "Python 3.14 alpha/beta schedule and final release target"}
    → Findings delivered to 'root'
  [agent-researcher] ⚙ exit_agent {"status": "success"}
    → Agent 'agent-researcher' terminated
  [root] ⚙ complete_task {"summary": "Extracted release dates from PEP 745"}

Python 3.14 is scheduled under PEP 745 with the final release targeted for October 2025...
```

### 3. Repository Inspection & File Operations

```text
oj> Inspect src/openjarvis/permissions.py and list the supported permission modes

  [root] ⚙ spawn_agent {"role": "coder", "task": "Inspect permissions.py for supported modes"}
    → Agent 'agent-coder' spawned
  [agent-coder] ⚙ search_in_files {"pattern": "def check", "path": "src/openjarvis/permissions.py"}
    → "Line 100: def check(self, tool_name: str, ...)"
  [agent-coder] ⚙ read_file {"file_path": "src/openjarvis/permissions.py", "start_line": 140, "line_count": 30}
    → "..."
  [agent-coder] ⚙ report_findings {"recipient": "root", "findings": "PermissionManager supports: interactive, autonomous, allowlist"}
    → Findings delivered to 'root'
  [agent-coder] ⚙ exit_agent {"status": "success"}
    → Agent 'agent-coder' terminated
  [root] ⚙ complete_task {"summary": "Extracted permission modes from permissions.py"}

`src/openjarvis/permissions.py` defines three operational modes:
1. `interactive`: Prompts user confirmation before executing unlisted tools.
2. `autonomous`: Automatically executes allowed tools, constrained by pattern rules and the safety classifier.
3. `allowlist`: Restricts automatic execution strictly to tools in `allowed_tools`.
```

---

## Event Trace Indicators

During execution, the CLI displays real-time event logs detailing agent lifecycle steps:

- `[<agent-id>] ⚙ spawn_agent`: A parent conductor creates a child agent with a specific role and task.
- `[<agent-id>] ⚙ connect_agents`: An agent establishes communication edges with another node in the graph topology.
- `[<agent-id>] ⚙ <tool_name>`: An agent executes a registered tool.
- `[<agent-id>] ⚙ report_findings`: An agent delivers intermediate results to a recipient mailbox.
- `[<agent-id>] ⚙ exit_agent`: An agent terminates its execution node.
- `[<agent-id>] ⚙ complete_task`: The root coordinator concludes task execution and outputs the final response.

---

## Non-Interactive & Scripted Usage

To run OpenJarvis headlessly (e.g., inside automated CI workflows or shell scripts), provide the prompt with `-p` and enable automatic tool approvals with `-y`:

```bash
openjarvis -y -p "Run pytest on tests/test_tools.py and report status"
```

---

## Next Steps

- **[Configuration Overview →](../configuration/overview.md)** — Customizing agent profiles and parameters.
- **[Multi-Agent Consensus & Topology →](../usage/routing.md)** — In-depth guide to the actor architecture.
- **[Security & Guardrails →](../security.md)** — Safety settings and argument validation.
