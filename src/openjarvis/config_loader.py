from __future__ import annotations

import logging
import os
from dataclasses import fields
from pathlib import Path

import yaml
from yaml import YAMLError

from openjarvis.model_types import (
    ConductorConfig,
    SpecialistConfig,
    ToolPermissionConfig,
    ToolRetrievalConfig,
)
from openjarvis.workspace import Workspace, discover_workspace

logger = logging.getLogger(__name__)

# Valid top-level keys for a `SpecialistConfig` dataclass
_VALID_KEYS = {f.name for f in fields(SpecialistConfig)}


def _build_specialist(name: str, spec: dict, section: str) -> SpecialistConfig:
    """Construct a SpecialistConfig, reporting unknown keys clearly."""
    if not isinstance(spec, dict):
        raise ValueError(f"{section} '{name}' must be a mapping, got {type(spec).__name__}")

    unknown = sorted(set(spec) - _VALID_KEYS)
    if unknown:
        raise ValueError(
            f"{section} '{name}' has unknown key(s): {', '.join(unknown)}. "
            f"Valid keys: {', '.join(sorted(_VALID_KEYS))}"
        )

    spec = {**spec, "name": spec.get("name", name)}
    if "system_prompt" not in spec:
        raise ValueError(f"{section} '{name}' is missing required key 'system_prompt'")

    return SpecialistConfig(**spec)


def _build_tool_retrieval(raw: dict | None) -> ToolRetrievalConfig:
    """Construct a ToolRetrievalConfig from dict."""
    if not raw or not isinstance(raw, dict):
        return ToolRetrievalConfig()
    valid_keys = {f.name for f in fields(ToolRetrievalConfig)}
    filtered = {k: v for k, v in raw.items() if k in valid_keys}
    return ToolRetrievalConfig(**filtered)


def _build_tool_permissions(raw: dict | None) -> ToolPermissionConfig:
    """Construct a ToolPermissionConfig from dict."""
    if not raw or not isinstance(raw, dict):
        return ToolPermissionConfig()
    valid_keys = {f.name for f in fields(ToolPermissionConfig)}
    filtered = {k: v for k, v in raw.items() if k in valid_keys}
    return ToolPermissionConfig(**filtered)


def locate_config() -> Path:
    """Locate config file in standard search locations.

    Search order:
    1. OJ_CONFIG environment variable (highest priority)
    2. Local project config: ./.openjarvis/config/specialists.yaml
    3. Global user config: ~/.openjarvis/config/specialists.yaml
    4. Current directory fallback: ./specialists.yaml
    5. Legacy user config fallback: ~/.config/openjarvis/specialists.yaml
    6. System config: /etc/openjarvis/specialists.yaml (Linux/macOS only)

    Raises:
        FileNotFoundError: If config not found in any location.
    """
    # 1. OJ_CONFIG env var (highest priority)
    if env_config := os.getenv("OJ_CONFIG"):
        config_path = Path(env_config)
        if config_path.exists():
            return config_path
        raise FileNotFoundError(
            f"OJ_CONFIG points to non-existent file: {env_config}"
        )

    # 2. Local project config (.openjarvis/config/specialists.yaml)
    local_config = Path.cwd() / ".openjarvis" / "config" / "specialists.yaml"
    if local_config.exists():
        return local_config

    # 3. Global user config (~/.openjarvis/config/specialists.yaml)
    global_config = Path.home() / ".openjarvis" / "config" / "specialists.yaml"
    if global_config.exists():
        return global_config

    # 4. Current directory fallback (./specialists.yaml)
    cwd_config = Path.cwd() / "specialists.yaml"
    if cwd_config.exists():
        return cwd_config

    # 5. Legacy user config directory (~/.config/openjarvis/specialists.yaml)
    legacy_user_config = Path.home() / ".config" / "openjarvis" / "specialists.yaml"
    if legacy_user_config.exists():
        return legacy_user_config

    # 6. System config (Linux/macOS only)
    if os.name != "nt":
        system_config = Path("/etc/openjarvis/specialists.yaml")
        if system_config.exists():
            return system_config

    # Config not found — build a helpful message listing all searched paths
    searched = [
        "  1. OJ_CONFIG environment variable (not set)",
        f"  2. {local_config}",
        f"  3. {global_config}",
        f"  4. {cwd_config} (legacy)",
        f"  5. {legacy_user_config} (legacy)",
    ]
    if os.name != "nt":
        searched.append(f"  6. {system_config}")
    searched_str = "\n".join(searched)
    raise FileNotFoundError(
        f"specialists.yaml not found!\n\nSearched locations:\n{searched_str}\n\n"
        "Run 'openjarvis' to launch the setup wizard, or set OJ_CONFIG=/path/to/config.yaml"
    )


def merge_configs(base: ConductorConfig, override: ConductorConfig) -> ConductorConfig:
    """Merge local override config on top of base global config."""
    # Generalist: override generalist if provided in override
    generalist = override.generalist

    # Specialists: copy base specialists, update/add from override
    specialists = dict(base.specialists)
    specialists.update(override.specialists)

    # Validate delegation targets
    for name, spec in specialists.items():
        for target in spec.delegates_to:
            if target != "generalist" and target not in specialists:
                raise ValueError(
                    f"specialist '{name}' delegates to '{target}', which is not "
                    f"defined in merged config. Known specialists: {', '.join(sorted(specialists))}, generalist"
                )

    # Max hops: override takes precedence if explicitly specified/different
    max_hops = override.max_hops if override.max_hops != 10 else base.max_hops

    # Tool retrieval & permissions: override if enabled or defined
    tool_retrieval = override.tool_retrieval if override.tool_retrieval.enabled else base.tool_retrieval
    tool_permissions = override.tool_permissions if override.tool_permissions.allowed_tools or override.tool_permissions.blocked_tools else base.tool_permissions

    return ConductorConfig(
        generalist=generalist,
        specialists=specialists,
        max_hops=max_hops,
        tool_retrieval=tool_retrieval,
        tool_permissions=tool_permissions,
    )


def _load_single_config(p: Path) -> ConductorConfig:
    """Load and parse a single YAML config file."""
    text = p.read_text(encoding="utf-8")
    try:
        raw = yaml.safe_load(text)
    except YAMLError as exc:
        raise ValueError(f"Error parsing YAML config {p}: {exc}") from exc

    if raw is None:
        raise ValueError(f"Config file {str(p)!r} is empty or contains no YAML document")

    if "generalist" not in raw:
        raise ValueError(f"Config {p} must have a 'generalist' section")

    generalist = _build_specialist("generalist", raw["generalist"], "generalist")

    specialists = {
        name: _build_specialist(name, spec, "specialist")
        for name, spec in (raw.get("specialists") or {}).items()
    }

    for name, spec in specialists.items():
        for target in spec.delegates_to:
            if target != "generalist" and target not in specialists:
                raise ValueError(
                    f"specialist '{name}' delegates to '{target}', which is not "
                    f"defined. Known specialists: {', '.join(sorted(specialists))}, generalist"
                )

    max_hops = raw.get("max_hops", ConductorConfig.max_hops)
    if not isinstance(max_hops, int) or isinstance(max_hops, bool) or max_hops < 1:
        raise ValueError(f"max_hops must be a positive integer, got {max_hops!r}")

    tool_retrieval = _build_tool_retrieval(raw.get("tool_retrieval"))
    tool_permissions = _build_tool_permissions(raw.get("tool_permissions"))

    return ConductorConfig(
        generalist=generalist,
        specialists=specialists,
        max_hops=max_hops,
        tool_retrieval=tool_retrieval,
        tool_permissions=tool_permissions,
    )


def load_config(
    path: str | Path | None = None,
    workspace: Workspace | None = None,
) -> ConductorConfig:
    """Load and validate YAML config file(s), merging local over global if applicable.

    Args:
        path: Path to config file. If None, searches standard locations and merges global/local.
        workspace: Optional Workspace instance.

    Returns:
        ConductorConfig object.

    Raises:
        FileNotFoundError: If config file not found.
        ValueError: If config file is invalid.
    """
    if path is not None:
        return _load_single_config(Path(path))

    ws = workspace or discover_workspace()
    global_file = ws.global_root / "config" / "specialists.yaml"
    local_file = ws.local_root / "config" / "specialists.yaml" if ws.local_root else None

    if global_file.exists() and local_file and local_file.exists():
        global_cfg = _load_single_config(global_file)
        local_cfg = _load_single_config(local_file)
        return merge_configs(global_cfg, local_cfg)

    # Fall back to standard locate_config()
    p = locate_config()
    return _load_single_config(p)


def get_delegation_mask(specialists: dict[str, SpecialistConfig]) -> dict[str, list[str]]:
    """Build delegation mask from specialist configs."""
    return {name: list(s.delegates_to) for name, s in specialists.items()}
