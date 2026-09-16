# Code Editor & Terminal Execution

Tools for file editing and shell execution complying with **SWE-bench**, **NVIDIA Open-SWE-Traces**, and terminal agent specifications.

---

## 1. File String Replacement Editor (`str_replace_editor`)

`str_replace_editor` is the standard editing interface used by Anthropic SWE-bench and Open-SWE-Traces. It provides atomic, exact-match text replacement with history tracking and undo capability.

- **Signature**: `(command: str, path: str, file_text: str = None, old_str: str = None, new_str: str = None, insert_line: int = None, view_range: list[int] = None) -> str`

### Commands:

1. **`view`**:
   Display numbered lines of a file.
   - `view_range`: Optional `[start_line, end_line]` range (1-indexed).
2. **`create`**:
   Create a new file with specified `file_text`. Overwrites if existing while saving undo state.
3. **`str_replace`**:
   Replace `old_str` with `new_str`. `old_str` must appear **uniquely** (exactly once) in the file. If `new_str` is omitted or empty, `old_str` is deleted.
4. **`insert`**:
   Insert `new_str` after `insert_line`. If `insert_line = 0`, new lines are prepended to the very beginning of the file.
5. **`undo_edit`**:
   Revert the last modification to `path` using session history.

---

## 2. Terminal Execution (`execute_bash` & `bash`)

### `execute_bash` / `bash`
Execute arbitrary bash shell commands inside a subprocess with execution timeouts, exit codes, and structured output.

- **Signature**: `(command: str, timeout_seconds: int = 30, cwd: str = None) -> str`
- Both `execute_bash` and `bash` are registered for full compatibility with benchmark agent prompts.
- Output includes exit code, stdout, and stderr.
