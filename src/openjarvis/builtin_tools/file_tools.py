import glob as glob_module
import os
import re

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
