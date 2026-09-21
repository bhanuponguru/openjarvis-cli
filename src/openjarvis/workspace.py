from __future__ import annotations

import contextlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Workspace:
    """Resolves global (~/.openjarvis) and local (./.openjarvis) directory paths and context files."""

    global_root: Path
    local_root: Path | None = None

    def global_path(self, *parts: str) -> Path:
        """Return a path relative to the global workspace root."""
        return self.global_root.joinpath(*parts)

    def local_path(self, *parts: str) -> Path | None:
        """Return a path relative to the local workspace root, or None if no local root."""
        if self.local_root is None:
            return None
        return self.local_root.joinpath(*parts)

    def config_path(self, filename: str) -> Path | None:
        """Find a configuration file by checking local then global config directories."""
        if self.local_root:
            local_file = self.local_root / "config" / filename
            if local_file.exists():
                return local_file
        global_file = self.global_root / "config" / filename
        if global_file.exists():
            return global_file
        return None

    def instructions(self) -> str:
        """Return merged global and local instructions markdown content."""
        parts: list[str] = []
        global_inst = self.global_root / "instructions.md"
        if global_inst.exists():
            try:
                content = global_inst.read_text(encoding="utf-8").strip()
                if content:
                    parts.append(content)
            except OSError:
                pass

        if self.local_root:
            local_inst = self.local_root / "instructions.md"
            if local_inst.exists():
                try:
                    content = local_inst.read_text(encoding="utf-8").strip()
                    if content:
                        parts.append(content)
                except OSError:
                    pass

        return "\n\n".join(parts)

    def context(self) -> str:
        """Return merged global and local context markdown content."""
        parts: list[str] = []
        global_ctx = self.global_root / "context.md"
        if global_ctx.exists():
            try:
                content = global_ctx.read_text(encoding="utf-8").strip()
                if content:
                    parts.append(content)
            except OSError:
                pass

        if self.local_root:
            local_ctx = self.local_root / "context.md"
            if local_ctx.exists():
                try:
                    content = local_ctx.read_text(encoding="utf-8").strip()
                    if content:
                        parts.append(content)
                except OSError:
                    pass

        return "\n\n".join(parts)

    def memory_dir(self, scope: str = "local") -> Path:
        """Return the memory directory path for the given scope (global or local)."""
        if scope == "global":
            mem_dir = self.global_root / "memory"
        else:
            if self.local_root:
                mem_dir = self.local_root / "memory"
            else:
                mem_dir = Path.cwd() / ".openjarvis" / "memory"
        with contextlib.suppress(OSError):
            mem_dir.mkdir(parents=True, exist_ok=True)
        return mem_dir

    def path(self, *parts: str) -> Path:
        """Return a path relative to local_root if present, otherwise global_root."""
        root = self.local_root or self.global_root
        return root.joinpath(*parts)

    def ensure_dirs(self) -> None:
        """Ensure standard subdirectories exist in the global workspace."""
        for sub in ("config", "memory", "vectors", "models", "artifacts"):
            with contextlib.suppress(OSError):
                (self.global_root / sub).mkdir(parents=True, exist_ok=True)
        if self.local_root:
            for sub in ("config", "memory", "vectors", "models", "artifacts"):
                with contextlib.suppress(OSError):
                    (self.local_root / sub).mkdir(parents=True, exist_ok=True)


_CURRENT_WORKSPACE: Workspace | None = None

def get_current_workspace() -> Workspace:
    global _CURRENT_WORKSPACE
    if _CURRENT_WORKSPACE is None:
        _CURRENT_WORKSPACE = discover_workspace()
    return _CURRENT_WORKSPACE


def set_current_workspace(ws: Workspace | None) -> None:
    """Set the active global workspace singleton."""
    global _CURRENT_WORKSPACE
    _CURRENT_WORKSPACE = ws


def discover_workspace(cwd: Path | None = None, home: Path | None = None) -> Workspace:
    """Discover or instantiate Workspace from environment, cwd, and user home."""
    global_dir = (home or Path.home()) / ".openjarvis"
    current_cwd = cwd or Path.cwd()

    local_dir: Path | None = current_cwd / ".openjarvis"
    if local_dir and not local_dir.exists():
        local_dir = None
        for parent in [current_cwd] + list(current_cwd.parents):
            candidate = parent / ".openjarvis"
            if candidate.exists() and candidate.is_dir() and candidate != global_dir:
                local_dir = candidate
                break

    return Workspace(global_root=global_dir, local_root=local_dir)
