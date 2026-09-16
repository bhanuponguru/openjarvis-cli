"""Native Git tools for OpenJarvis.

Provides standard tools for version control and patch management:
- git_diff: Unified diff inspection of working tree or staged changes
- git_status: Short status summary of modified and untracked files
- git_log: Compact commit history inspection
- apply_patch: Apply unified diff patches cleanly
"""

from __future__ import annotations

import subprocess

from openjarvis.tools import tool


@tool()
def git_diff(path: str = "", cached: bool = False) -> str:
    """Get the current git diff of working tree changes.

    Args:
        path: Optional specific file path or subdirectory to inspect diff for.
        cached: If True, inspect staged changes (--cached); otherwise unstaged.

    Returns:
        Unified git diff output string or error message.
    """
    cmd = ["git", "diff"]
    if cached:
        cmd.append("--cached")
    if path:
        cmd.extend(["--", path])

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode != 0:
            return f"Git error (exit code {res.returncode}): {res.stderr.strip()}"
        out = res.stdout.strip()
        return out if out else "(No git diff changes detected)"
    except Exception as exc:
        return f"Error executing git diff: {exc}"


@tool()
def git_status() -> str:
    """Get the current working directory git status.

    Returns:
        Formatted git status short summary.
    """
    try:
        res = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, timeout=10)
        if res.returncode != 0:
            return f"Git error (exit code {res.returncode}): {res.stderr.strip()}"
        out = res.stdout.strip()
        return out if out else "Working tree clean (no untracked or modified files)"
    except Exception as exc:
        return f"Error executing git status: {exc}"


@tool()
def git_log(max_count: int = 5) -> str:
    """View recent git commit logs.

    Args:
        max_count: Number of recent commits to display (default 5, max 20).

    Returns:
        Formatted git log output.
    """
    count = min(max(1, max_count), 20)
    try:
        res = subprocess.run(
            ["git", "log", f"-n{count}", "--oneline", "--decorate"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode != 0:
            return f"Git error (exit code {res.returncode}): {res.stderr.strip()}"
        return res.stdout.strip() if res.stdout.strip() else "(No commits found)"
    except Exception as exc:
        return f"Error executing git log: {exc}"


@tool()
def apply_patch(patch: str) -> str:
    """Apply a unified diff patch to the repository.

    Args:
        patch: Unified diff patch text (format produced by git diff).

    Returns:
        Confirmation message or error details.
    """
    if not patch.strip():
        return "Error: Empty patch provided."

    try:
        proc = subprocess.run(
            ["git", "apply", "-"],
            input=patch,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            return "Successfully applied patch."
        return f"Patch application failed (exit code {proc.returncode}):\n{proc.stderr.strip()}"
    except Exception as exc:
        return f"Error applying patch: {exc}"
