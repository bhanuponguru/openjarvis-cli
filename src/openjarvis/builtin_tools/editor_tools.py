"""Native SWE-bench and NVIDIA Open-SWE-Traces string-replace editor tool.

Provides str_replace_editor supporting view, create, str_replace, insert, and undo_edit
with 1-indexed line viewing and exact unique-match safety.
"""

import os
import subprocess
from pathlib import Path

from openjarvis.tools import tool

_UNDO_HISTORY: dict[str, list[str]] = {}


def _get_history(path: str) -> list[str]:
    p = str(Path(path).resolve())
    if p not in _UNDO_HISTORY:
        _UNDO_HISTORY[p] = []
    return _UNDO_HISTORY[p]


@tool()
def str_replace_editor(
    command: str,
    path: str,
    file_text: str | None = None,
    old_str: str | None = None,
    new_str: str | None = None,
    insert_line: int | None = None,
    view_range: list[int] | None = None,
) -> str:
    """Standard SWE benchmark file editor interface.

    Args:
        command: One of 'view', 'create', 'str_replace', 'insert', 'undo_edit'.
        path: Absolute or relative path to the file.
        file_text: Full file content (used with 'create').
        old_str: Target string to replace (must be unique in file, used with 'str_replace').
        new_str: Replacement or inserted content (used with 'str_replace' and 'insert').
        insert_line: Line number after which new_str will be inserted (1-indexed, used with 'insert').
        view_range: Optional [start_line, end_line] 1-indexed range (used with 'view').

    Returns:
        Status message or rendered file content.
    """
    file_path = Path(path)

    if command == "view":
        if not file_path.exists():
            return f"Error: File '{path}' does not exist."
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            total_lines = len(lines)

            if view_range is not None and len(view_range) == 2:
                start, end = view_range
                start = max(1, start)
                end = min(total_lines, end)
                selected = lines[start - 1 : end]
                numbered = [f"{i:6d} | {line}" for i, line in enumerate(selected, start=start)]
            else:
                numbered = [f"{i:6d} | {line}" for i, line in enumerate(lines, start=1)]

            return "\n".join(numbered) if numbered else "(Empty file)"
        except Exception as e:
            return f"Error viewing file '{path}': {e}"

    elif command == "create":
        if file_text is None:
            return "Error: 'file_text' must be provided for 'create' command."
        try:
            if file_path.exists():
                _get_history(path).append(file_path.read_text(encoding="utf-8", errors="replace"))
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_text, encoding="utf-8")
            return f"File created successfully at '{path}'."
        except Exception as e:
            return f"Error creating file '{path}': {e}"

    elif command == "str_replace":
        if not file_path.exists():
            return f"Error: File '{path}' does not exist."
        if old_str is None:
            return "Error: 'old_str' must be provided for 'str_replace'."
        replacement = new_str if new_str is not None else ""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            count = content.count(old_str)
            if count == 0:
                return f"Error: 'old_str' not found in '{path}'."
            if count > 1:
                return (
                    f"Error: 'old_str' appears {count} times in '{path}'. "
                    "Replacement requires a uniquely matching string."
                )

            # Save undo state
            _get_history(path).append(content)
            new_content = content.replace(old_str, replacement, 1)
            file_path.write_text(new_content, encoding="utf-8")
            return f"Successfully replaced text in '{path}'."
        except Exception as e:
            return f"Error modifying file '{path}': {e}"

    elif command == "insert":
        if not file_path.exists():
            return f"Error: File '{path}' does not exist."
        if insert_line is None or new_str is None:
            return "Error: Both 'insert_line' and 'new_str' must be provided for 'insert'."
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            _get_history(path).append(content)

            target_idx = max(0, min(len(lines), insert_line))
            new_lines = new_str.splitlines()
            lines[target_idx:target_idx] = new_lines
            file_path.write_text("\n".join(lines) + ("\n" if content.endswith("\n") else ""), encoding="utf-8")
            return f"Successfully inserted text at line {insert_line} in '{path}'."
        except Exception as e:
            return f"Error inserting into file '{path}': {e}"

    elif command == "undo_edit":
        history = _get_history(path)
        if not history:
            return f"Error: No previous edits recorded for '{path}'."
        previous_content = history.pop()
        try:
            file_path.write_text(previous_content, encoding="utf-8")
            return f"Successfully reverted last edit on '{path}'."
        except Exception as e:
            return f"Error restoring '{path}': {e}"

    return f"Error: Unknown command '{command}'. Supported: view, create, str_replace, insert, undo_edit."


@tool()
def execute_bash(
    command: str,
    timeout_seconds: int = 30,
    cwd: str | None = None,
) -> str:
    """Execute a bash command in a subprocess, returning exit code, stdout, and stderr.

    Args:
        command: Bash command line string to execute.
        timeout_seconds: Execution timeout in seconds (default 30).
        cwd: Working directory for execution (defaults to current working directory).

    Returns:
        Formatted execution result containing exit code, stdout, and stderr.
    """
    work_dir = cwd or os.getcwd()
    try:
        res = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=work_dir,
        )
        out = [f"Exit code: {res.returncode}"]
        if res.stdout:
            out.append(f"Stdout:\n{res.stdout.strip()}")
        if res.stderr:
            out.append(f"Stderr:\n{res.stderr.strip()}")
        if not res.stdout and not res.stderr:
            out.append("(no output)")
        return "\n".join(out)
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout_seconds} seconds"
    except Exception as e:
        return f"Error executing bash command: {e}"


@tool()
def bash(
    command: str,
    timeout_seconds: int = 30,
    cwd: str | None = None,
) -> str:
    """Standard SWE benchmark bash execution interface.

    Args:
        command: Bash command line string to execute.
        timeout_seconds: Execution timeout in seconds (default 30).
        cwd: Working directory for execution (defaults to current working directory).

    Returns:
        Formatted execution result containing exit code, stdout, and stderr.
    """
    return execute_bash(command=command, timeout_seconds=timeout_seconds, cwd=cwd)

