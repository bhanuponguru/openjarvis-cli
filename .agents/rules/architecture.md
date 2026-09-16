# Architecture & Component Guidelines — openjarvis-cli

## 1. Conductor & State Graph
- `openjarvis.conductor.Conductor`: Central coordinator that manages conversation sessions, speaker histories, and specialist delegation.
- `openjarvis.graph`: Implements the Heterogeneous Cognitive Graph on LangGraph:
  - `protocol.py`: Typed directive and observation messages (`ActDirectiveMessage`, `ActObservationMessage`).
  - `blackboard.py`: `StateBlackboard` for sharing state across specialists with cycle detection and observation compaction.
  - `engine.py`: Graph state machine driving execution steps.

## 2. Built-in Tools Framework (`openjarvis.builtin_tools`)
OpenJarvis CLI ships with 49 native tools organized into 9 modules:
- **Editor & Terminal (`editor_tools`)**: `execute_bash`, `bash`, and `str_replace_editor` (view, create, str_replace, insert, undo_edit).
- **Git & Version Control (`git_tools`)**: `git_diff`, `git_status`, `git_log`, `apply_patch`.
- **File System (`file_tools`)**: `read_file`, `write_file`, `list_directory`, `search_in_files`, `search_dir`, `search_file`, `find_file`, `file_info`, `delete_file`.
- **Web & API (`web_tools`)**: `web_search`, `fetch_url`, `fetch_wikipedia`, `http_request`, `parse_openapi_spec`.
- **Code Execution (`code_tools`)**: `run_python`, `run_shell`, `lint_python`, `run_pytest`.
- **Data Processing (`data_tools`)**: `parse_json`, `jq_query`, `parse_csv`, `regex_search`, `regex_replace`, `sql_query`.
- **Persistent Memory (`memory_tools`)**: `save_memory`, `read_memory`, `update_memory`, `delete_memory`, `list_memories`, `search_memories`, and backward-compatible note aliases.
- **Date, Time & Math (`datetime_tools`, `math_tools`)**: date/time manipulation and formatting, AST-safe math calculators, unit converters, equation solvers, statistics.

## 3. Tool Permissions & Security Sandbox (`openjarvis.permissions`)
- `PermissionManager`: Intercepts every tool call before execution.
- Configurable approval modes: `prompt`, `auto_allow`, `deny_all`.
- Argument pattern filters: Enforce directory sandboxing (e.g. restrict write operations to current workspace).

## 4. Package Boundary Invariants
- `openjarvis-cli` must NEVER import `torch` or model internals.
- All model interaction occurs through HTTP or LangChain provider abstractions (`ChatOpenAI`, `ChatOllama`, `ChatAnthropic`).

