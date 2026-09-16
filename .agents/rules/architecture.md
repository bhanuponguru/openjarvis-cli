# Architecture & Component Guidelines — openjarvis-cli

## 1. Conductor & State Graph
- `openjarvis.conductor.Conductor`: Central coordinator that manages conversation sessions, speaker histories, and specialist delegation.
- `openjarvis.graph`: Implements the Heterogeneous Cognitive Graph on LangGraph:
  - `protocol.py`: Typed directive and observation messages (`ActDirectiveMessage`, `ActObservationMessage`).
  - `blackboard.py`: `StateBlackboard` for sharing state across specialists with cycle detection and observation compaction.
  - `engine.py`: Graph state machine driving execution steps.

## 2. Built-in Tools Framework (`openjarvis.builtin_tools`)
OpenJarvis CLI ships with 29 native tools:
- **Terminal Execution**: `execute_bash` with timeout enforcement, sandboxed execution, and structured stdout/stderr capturing.
- **File System & Code Editing**: `str_replace_editor` (view, create, str_replace, insert, undo_edit) matching SWE-bench specifications.
- **Persistent Memory**: `store_memory`, `retrieve_memory`, `delete_memory` with local JSON and global session scoping.
- **Information Retrieval**: `web_search`, `fetch_web_page`, `extract_text`.
- **System Utilities**: date/time, JSON validators, calculation utilities.

## 3. Tool Permissions & Security Sandbox (`openjarvis.permissions`)
- `PermissionManager`: Intercepts every tool call before execution.
- Configurable approval modes: `prompt`, `auto_allow`, `deny_all`.
- Argument pattern filters: Enforce directory sandboxing (e.g. restrict write operations to current workspace).

## 4. Package Boundary Invariants
- `openjarvis-cli` must NEVER import `torch` or model internals.
- All model interaction occurs through HTTP or LangChain provider abstractions (`ChatOpenAI`, `ChatOllama`, `ChatAnthropic`).

