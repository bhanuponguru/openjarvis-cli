import fnmatch
import glob as glob_module
import os
import re
from pathlib import Path
from typing import Any

from openjarvis.tools import tool


@tool()
def read_file(path: str, max_chars: int = 8000) -> str:
    """Read the contents of a text file.

    Args:
        path: File path (relative to current working directory).
        max_chars: Maximum number of characters to read (truncates if exceeded).

    Returns:
        File contents, truncated if necessary.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
        if len(content) == max_chars:
            content += f"\n... [truncated at {max_chars} chars]"
        return content
    except Exception as e:
        return f"Error reading file: {e}"

@tool()
def write_file(path: str, content: str, append: bool = False) -> str:
    """Write content to a file.

    Args:
        path: File path (relative to current working directory).
        content: Content to write.
        append: If True, append to existing file; if False, overwrite.

    Returns:
        Success or error message.
    """
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        action = "appended to" if append else "wrote to"
        return f"Successfully {action} {path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool()
def list_directory(path: str = ".", pattern: str = "*") -> list[str]:
    """List files and directories matching a glob pattern.

    Args:
        path: Directory path (relative to current working directory).
        pattern: Glob pattern (e.g., "*.py", "**/*.txt").

    Returns:
        Sorted list of matching paths.
    """
    try:
        full_pattern = os.path.join(path, pattern)
        matches = sorted(glob_module.glob(full_pattern, recursive=True))
        return matches if matches else [f"No matches for {full_pattern}"]
    except Exception as e:
        return [f"Error listing directory: {e}"]

@tool()
def search_in_files(path: str, pattern: str, glob: str = "**/*") -> list[dict]:
    """Search for a regex pattern in files matching a glob.

    Args:
        path: Base directory to search in.
        pattern: Regular expression pattern to search for.
        glob: Glob pattern for files to search (e.g., "**/*.py").

    Returns:
        List of dicts with 'file', 'line_num', and 'match' keys. Limited to first 100 matches.
    """
    try:
        regex = re.compile(pattern)
        results = []

        full_glob = os.path.join(path, glob)
        for file_path in glob_module.glob(full_glob, recursive=True):
            if not os.path.isfile(file_path):
                continue

            try:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    for line_num, line in enumerate(f, 1):
                        for match in regex.finditer(line):
                            results.append({
                                "file": file_path,
                                "line_num": line_num,
                                "match": match.group(0),
                            })
                            if len(results) >= 100:
                                break
                        if len(results) >= 100:
                            break
            except Exception:
                pass

            if len(results) >= 100:
                break

        return results if results else [{"error": f"No matches for pattern '{pattern}'"}]
    except Exception as e:
        return [{"error": str(e)}]

@tool()
def file_info(path: str) -> dict:
    """Get metadata about a file or directory.

    Args:
        path: File or directory path.

    Returns:
        Dict with 'size' (bytes), 'mtime' (ISO timestamp), 'type' ('file' or 'directory').
    """
    try:
        stat = os.stat(path)
        import datetime
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
        file_type = "directory" if os.path.isdir(path) else "file"

        return {
            "path": path,
            "type": file_type,
            "size_bytes": stat.st_size,
            "mtime": mtime,
        }
    except Exception as e:
        return {"error": str(e)}

@tool()
def delete_file(path: str) -> str:
    """Delete a file.

    Args:
        path: File path to delete.

    Returns:
        Success or error message.
    """
    try:
        if os.path.isdir(path):
            return "Error: path is a directory, not a file. Use file deletion only for files."
        os.remove(path)
        return f"Successfully deleted {path}"
    except Exception as e:
        return f"Error deleting file: {e}"


@tool()
def search_dir(search_term: str, dir_path: str = ".") -> list[dict[str, Any]]:
    """Recursively search for a string or regex pattern across files in a directory.

    Args:
        search_term: Regular expression or literal string to match.
        dir_path: Root directory to search within (default current directory).

    Returns:
        List of dicts with 'file', 'line', and 'content' keys (up to 100 matches).
    """
    root = Path(dir_path)
    if not root.exists():
        return [{"error": f"Directory '{dir_path}' does not exist."}]

    try:
        pattern = re.compile(search_term)
    except re.error as exc:
        return [{"error": f"Invalid regex pattern '{search_term}': {exc}"}]

    matches: list[dict[str, Any]] = []
    for cur_root, dirs, files in os.walk(str(root)):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "site-packages")
        ]
        for file_name in files:
            if file_name.startswith("."):
                continue
            file_path = Path(cur_root) / file_name
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    for line_idx, line in enumerate(f, start=1):
                        if pattern.search(line):
                            matches.append({
                                "file": str(file_path),
                                "line": line_idx,
                                "content": line.rstrip()[:200],
                            })
                            if len(matches) >= 100:
                                return matches
            except OSError:
                continue

    return matches if matches else [{"message": f"No matches found for '{search_term}'."}]


@tool()
def search_file(search_term: str, file_path: str) -> list[dict[str, Any]]:
    """Search for a string or regex pattern in a specific file.

    Args:
        search_term: Regular expression or literal string to match.
        file_path: Path to the target file.

    Returns:
        List of dicts with 'line' and 'content' keys.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return [{"error": f"File '{file_path}' does not exist or is not a file."}]

    try:
        pattern = re.compile(search_term)
    except re.error as exc:
        return [{"error": f"Invalid regex pattern '{search_term}': {exc}"}]

    matches: list[dict[str, Any]] = []
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for line_idx, line in enumerate(f, start=1):
                if pattern.search(line):
                    matches.append({
                        "line": line_idx,
                        "content": line.rstrip()[:300],
                    })
                    if len(matches) >= 100:
                        break
        return matches if matches else [
            {"message": f"No matches found in '{file_path}' for '{search_term}'."}
        ]
    except Exception as exc:
        return [{"error": f"Error searching in file '{file_path}': {exc}"}]


@tool()
def find_file(file_name: str, dir_path: str = ".") -> list[str]:
    """Find files matching a filename or glob pattern in a directory tree.

    Args:
        file_name: Filename or glob pattern (e.g., "test_*.py" or "conductor.py").
        dir_path: Root directory to search within (default current directory).

    Returns:
        Sorted list of relative file paths matching the pattern.
    """
    root = Path(dir_path)
    if not root.exists():
        return [f"Error: Directory '{dir_path}' does not exist."]

    matches: list[str] = []
    for cur_root, dirs, files in os.walk(str(root)):
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("__pycache__", "node_modules", "site-packages")
        ]
        for f in files:
            if fnmatch.fnmatch(f, file_name):
                rel_path = os.path.relpath(os.path.join(cur_root, f), str(root))
                matches.append(rel_path)
                if len(matches) >= 100:
                    break
        if len(matches) >= 100:
            break

    return sorted(matches) if matches else [f"No files matching '{file_name}' found in '{dir_path}'."]
