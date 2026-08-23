from __future__ import annotations

import re
from pathlib import Path

from openjarvis.tools import tool
from openjarvis.workspace import get_current_workspace


def _sanitize_name(name: str) -> str:
    """Sanitize memory file name to prevent path traversal and invalid characters."""
    cleaned = name.strip()
    if cleaned.endswith(".md"):
        cleaned = cleaned[:-3]
    # Replace path separators and unwanted characters
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", cleaned)
    # Prevent leading dots or empty names
    cleaned = cleaned.lstrip(".")
    if not cleaned:
        cleaned = "memory"
    return cleaned


def _get_target_file(name: str, scope: str = "local") -> Path:
    ws = get_current_workspace()
    mem_dir = ws.memory_dir(scope=scope if scope in ("global", "local") else "local")
    sanitized = _sanitize_name(name)
    return mem_dir / f"{sanitized}.md"


@tool()
def save_memory(name: str, content: str, scope: str = "local") -> str:
    """Create or overwrite a persistent memory file in markdown format.

    Args:
        name: Name of the memory topic or note (without extension).
        content: Markdown text content to persist.
        scope: Storage scope, either 'local' (project-specific) or 'global' (user-wide). Defaults to 'local'.

    Returns:
        Confirmation message with file location.
    """
    target = _get_target_file(name, scope=scope)
    target.write_text(content, encoding="utf-8")
    return f"Saved memory '{target.stem}' in {scope} scope ({target})"


@tool()
def read_memory(name: str, scope: str = "local") -> str:
    """Read the contents of a persistent memory file.

    Args:
        name: Name of the memory note to read.
        scope: Storage scope, either 'local' (project-specific) or 'global' (user-wide). Defaults to 'local'.

    Returns:
        The markdown content of the memory, or an error message if not found.
    """
    target = _get_target_file(name, scope=scope)
    if not target.exists():
        # If not found in local, try global scope as a fallback
        if scope == "local":
            global_target = _get_target_file(name, scope="global")
            if global_target.exists():
                return global_target.read_text(encoding="utf-8")
        return f"Error: Memory '{name}' not found in {scope} scope"
    return target.read_text(encoding="utf-8")


@tool()
def update_memory(name: str, content: str, scope: str = "local") -> str:
    """Append or update information in an existing memory file.

    Args:
        name: Name of the memory note to update.
        content: New content to append.
        scope: Storage scope ('local' or 'global'). Defaults to 'local'.

    Returns:
        Confirmation message.
    """
    target = _get_target_file(name, scope=scope)
    if target.exists():
        existing = target.read_text(encoding="utf-8").rstrip()
        new_text = f"{existing}\n\n{content}"
    else:
        new_text = content
    target.write_text(new_text, encoding="utf-8")
    return f"Updated memory '{target.stem}' in {scope} scope"


@tool()
def delete_memory(name: str, scope: str = "local") -> str:
    """Delete a persistent memory file.

    Args:
        name: Name of the memory note to delete.
        scope: Storage scope ('local' or 'global'). Defaults to 'local'.

    Returns:
        Confirmation or error message.
    """
    target = _get_target_file(name, scope=scope)
    if target.exists():
        target.unlink()
        return f"Deleted memory '{target.stem}' from {scope} scope"
    return f"Error: Memory '{name}' not found in {scope} scope"


@tool()
def list_memories(scope: str = "local") -> list[str]:
    """List all available persistent memory files in the given scope.

    Args:
        scope: Storage scope to list ('local', 'global', or 'all'). Defaults to 'local'.

    Returns:
        List of memory note names.
    """
    ws = get_current_workspace()
    results: list[str] = []

    scopes = ["local", "global"] if scope == "all" else [scope if scope in ("local", "global") else "local"]
    for s in scopes:
        mem_dir = ws.memory_dir(scope=s)
        if mem_dir.exists():
            for f in sorted(mem_dir.glob("*.md")):
                prefix = f"[{s}] " if scope == "all" else ""
                results.append(f"{prefix}{f.stem}")

    return results


@tool()
def search_memories(query: str, scope: str = "all") -> list[dict]:
    """Search across memory files for matching text queries.

    Args:
        query: Search term or keyword.
        scope: Search scope ('local', 'global', or 'all'). Defaults to 'all'.

    Returns:
        List of dictionaries with name, scope, and matching snippets.
    """
    ws = get_current_workspace()
    scopes = ["local", "global"] if scope == "all" else [scope if scope in ("local", "global") else "local"]
    matches: list[dict] = []
    q_lower = query.lower()

    for s in scopes:
        mem_dir = ws.memory_dir(scope=s)
        if mem_dir.exists():
            for f in sorted(mem_dir.glob("*.md")):
                try:
                    text = f.read_text(encoding="utf-8")
                    if q_lower in text.lower():
                        # Extract first matching line or snippet
                        lines = [line for line in text.splitlines() if q_lower in line.lower()]
                        snippet = lines[0] if lines else text[:150]
                        matches.append({
                            "name": f.stem,
                            "scope": s,
                            "snippet": snippet.strip(),
                        })
                except OSError:
                    continue

    return matches


# Backward-compatible aliases for existing session notes API
@tool()
def store_note(key: str, content: str) -> str:
    """Store a note in persistent local memory."""
    return save_memory(name=key, content=content, scope="local")


@tool()
def recall_note(key: str) -> str:
    """Retrieve a stored note from memory."""
    return read_memory(name=key, scope="local")


@tool()
def list_notes() -> list[str]:
    """List all stored note names in local memory."""
    return list_memories(scope="local")


@tool()
def delete_note(key: str) -> str:
    """Delete a stored note from local memory."""
    return delete_memory(name=key, scope="local")
