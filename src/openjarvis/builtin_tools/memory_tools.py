from openjarvis.tools import tool

_session_notes: dict[str, str] = {}

@tool()
def store_note(key: str, content: str) -> str:
    """Store a note in session memory.

    Args:
        key: Note key/name.
        content: Note content.

    Returns:
        Confirmation message.
    """
    _session_notes[key] = content
    return f"Stored note '{key}'"

@tool()
def recall_note(key: str) -> str:
    """Retrieve a stored note from session memory.

    Args:
        key: Note key/name.

    Returns:
        Note content or error message if not found.
    """
    if key in _session_notes:
        return _session_notes[key]
    return f"Error: Note '{key}' not found"

@tool()
def list_notes() -> list[str]:
    """List all stored note keys.

    Returns:
        List of note keys, or empty list if no notes stored.
    """
    return sorted(_session_notes.keys())

@tool()
def delete_note(key: str) -> str:
    """Delete a stored note.

    Args:
        key: Note key/name to delete.

    Returns:
        Confirmation or error message.
    """
    if key in _session_notes:
        del _session_notes[key]
        return f"Deleted note '{key}'"
    return f"Error: Note '{key}' not found"
