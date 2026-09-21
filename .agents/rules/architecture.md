# Architecture & Component Guidelines — openjarvis-cli

## 1. Multi-Agent System (MAS) & Conductor Graph
- `openjarvis.multiagent.MultiAgentSystem`: Top-level asynchronous actor engine orchestrating dynamic agent graphs, task mailboxes, and strict bottom-up completion.
- `openjarvis.multiagent.DynamicAgentGraph`: Manages parent-child topology, arbitrary communication edges, and enforces child exit preconditions before parent exit.
- `openjarvis.artifacts.ArtifactStore`: Manages dual persistence of structured deliverables in memory and `.openjarvis/artifacts/`.
- `openjarvis.conductor.Conductor`: Autonomous agent node engine executing inner LangGraph routing and specialist delegation.
- `openjarvis.graph`: Directed Cognitive Graph components (`blackboard.py`, `protocol.py`, `engine.py`).

## 2. Built-in Tools Framework (`openjarvis.builtin_tools`)
OpenJarvis CLI ships with 49 native tools organized into 9 modules:
- **Editor & Terminal (`editor_tools`)**: `execute_bash`, `bash`, and `str_replace_editor` (view, create, str_replace, insert, undo_edit).
- **Git & Version Control (`git_tools`)**: `git_diff`, `git_status`, `git_log`, `apply_patch`.
- **File System (`file_tools`)**: `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file`.
- **Web & API (`web_tools`)**: `search_web`, `fetch_url`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec`.
- **Code Execution (`code_tools`)**: `run_python`, `run_shell`, `lint_python`, `run_pytest`.
- **Data Processing (`data_tools`)**: `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query`.
- **Persistent Memory (`memory_tools`)**: `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and backward-compatible note aliases.
- **Date, Time & Math (`datetime_tools`, `math_tools`)**: date/time manipulation and formatting, AST-safe math calculators, unit converters, equation solvers, statistics.

## 3. Tool Permissions & Security Sandbox (`openjarvis.permissions`)
- `PermissionManager`: Intercepts every tool call before execution.
- Configurable approval modes: `interactive`, `autonomous`, `allowlist`.
- MAS meta-tools (`spawn_agent`, `connect_agents`, `report_findings`, `exit_agent`, `complete_task`) exempt from confirmation prompts.
- Argument pattern filters: Enforce parameter matching and directory constraints using `fnmatch`.

## 4. Package Boundary Invariants
- `openjarvis-cli` must NEVER import `torch` or model internals.
- All model interaction occurs through HTTP or LangChain provider abstractions (`ChatOpenAI`, `ChatOllama`, `ChatAnthropic`).

