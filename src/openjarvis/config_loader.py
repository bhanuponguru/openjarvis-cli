from __future__ import annotations

import logging
import os
from dataclasses import fields
from pathlib import Path

import yaml
from yaml import YAMLError

from openjarvis.model_types import (
    AgentProfileConfig,
    ConductorConfig,
    MultiAgentLimitsConfig,
    SpecialistConfig,
    ToolPermissionConfig,
    ToolRetrievalConfig,
)
from openjarvis.workspace import Workspace, discover_workspace

logger = logging.getLogger(__name__)

# Valid top-level keys for dataclasses
_VALID_SPECIALIST_KEYS = {f.name for f in fields(SpecialistConfig)}
_VALID_AGENT_KEYS = {f.name for f in fields(AgentProfileConfig)}
_VALID_LIMITS_KEYS = {f.name for f in fields(MultiAgentLimitsConfig)}


def _build_specialist(name: str, spec: dict, section: str) -> SpecialistConfig:
    """Construct a SpecialistConfig, reporting unknown keys clearly."""
    if not isinstance(spec, dict):
        raise ValueError(f"{section} '{name}' must be a mapping, got {type(spec).__name__}")

    unknown = sorted(set(spec) - _VALID_SPECIALIST_KEYS)
    if unknown:
        raise ValueError(
            f"{section} '{name}' has unknown key(s): {', '.join(unknown)}. "
            f"Valid keys: {', '.join(sorted(_VALID_SPECIALIST_KEYS))}"
        )

    spec = {**spec, "name": spec.get("name", name)}
    if "system_prompt" not in spec:
        raise ValueError(f"{section} '{name}' is missing required key 'system_prompt'")

    if "tools" in spec and spec["tools"] is not None and (
        not isinstance(spec["tools"], list) or any(not isinstance(t, str) for t in spec["tools"])
    ):
        raise ValueError(f"{section} '{name}' key 'tools' must be a list of strings or null")

    if "description" in spec and spec["description"] is not None and not isinstance(spec["description"], str):
        raise ValueError(f"{section} '{name}' key 'description' must be a string or null")

    return SpecialistConfig(**spec)


def _build_agent_profile(name: str, spec: dict, section: str = "agent") -> AgentProfileConfig:
    """Construct an AgentProfileConfig, reporting unknown keys clearly."""
    if not isinstance(spec, dict):
        raise ValueError(f"{section} '{name}' must be a mapping, got {type(spec).__name__}")

    unknown = sorted(set(spec) - _VALID_AGENT_KEYS)
    if unknown:
        raise ValueError(
            f"{section} '{name}' has unknown key(s): {', '.join(unknown)}. "
            f"Valid keys: {', '.join(sorted(_VALID_AGENT_KEYS))}"
        )

    spec = {**spec, "name": spec.get("name", name)}
    if "system_prompt" not in spec:
        spec["system_prompt"] = f"You are the {name} agent in OpenJarvis."

    return AgentProfileConfig(**spec)


def _build_limits(raw: dict | None) -> MultiAgentLimitsConfig:
    """Construct MultiAgentLimitsConfig from dict."""
    if not raw or not isinstance(raw, dict):
        return MultiAgentLimitsConfig()
    filtered = {k: v for k, v in raw.items() if k in _VALID_LIMITS_KEYS}
    return MultiAgentLimitsConfig(**filtered)


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
    2. Local workspace config: ./.openjarvis/config.yaml or ./.openjarvis/config/config.yaml
    3. Global user config: ~/.openjarvis/config.yaml or ~/.openjarvis/config/config.yaml
    4. System config: /etc/openjarvis/config.yaml (Linux/macOS only)

    Raises:
        FileNotFoundError: If config not found in any location.
    """
    if env_config := os.getenv("OJ_CONFIG"):
        config_path = Path(env_config)
        if config_path.exists():
            return config_path
        raise FileNotFoundError(
            f"OJ_CONFIG points to non-existent file: {env_config}"
        )

    # Local workspace candidates
    for cand in [
        Path.cwd() / ".openjarvis" / "config.yaml",
        Path.cwd() / ".openjarvis" / "config" / "config.yaml",
    ]:
        if cand.exists():
            return cand

    # Global user candidates
    for cand in [
        Path.home() / ".openjarvis" / "config.yaml",
        Path.home() / ".openjarvis" / "config" / "config.yaml",
    ]:
        if cand.exists():
            return cand

    if os.name != "nt":
        system_config = Path("/etc/openjarvis/config.yaml")
        if system_config.exists():
            return system_config

    searched = [
        "  1. OJ_CONFIG environment variable (not set)",
        f"  2. {Path.cwd() / '.openjarvis' / 'config.yaml'}",
        f"  3. {Path.home() / '.openjarvis' / 'config.yaml'}",
    ]
    if os.name != "nt":
        searched.append(f"  4. {Path('/etc/openjarvis/config.yaml')}")
    searched_str = "\n".join(searched)
    raise FileNotFoundError(
        f"OpenJarvis config.yaml not found!\n\nSearched locations:\n{searched_str}\n\n"
        "Run 'openjarvis' to launch the setup wizard, or set OJ_CONFIG=/path/to/config.yaml"
    )


def merge_configs(base: ConductorConfig, override: ConductorConfig) -> ConductorConfig:
    """Merge local override config on top of base global config."""
    root_agent = override.root_agent or base.root_agent
    generalist = override.generalist if override.generalist.system_prompt else base.generalist

    agents = dict(base.agents)
    agents.update(override.agents)

    specialists = dict(base.specialists)
    specialists.update(override.specialists)

    for name, spec in specialists.items():
        for target in spec.delegates_to:
            if target != "generalist" and target not in specialists:
                raise ValueError(
                    f"specialist '{name}' delegates to '{target}', which is not "
                    f"defined in merged config. Known specialists: {', '.join(sorted(specialists))}, generalist"
                )

    max_hops = override.max_hops if override.max_hops != 10 else base.max_hops
    tool_retrieval = override.tool_retrieval if override.tool_retrieval.enabled else base.tool_retrieval
    tool_permissions = (
        override.tool_permissions
        if override.tool_permissions.allowed_tools or override.tool_permissions.blocked_tools
        else base.tool_permissions
    )
    limits = override.limits if override.limits != MultiAgentLimitsConfig() else base.limits

    return ConductorConfig(
        root_agent=root_agent,
        agents=agents,
        generalist=generalist,
        specialists=specialists,
        max_hops=max_hops,
        tool_retrieval=tool_retrieval,
        tool_permissions=tool_permissions,
        limits=limits,
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

    root_raw = raw.get("root_agent")
    gen_raw = raw.get("generalist")

    if not root_raw and not gen_raw:
        raise ValueError(f"Config {p} must have a 'root_agent' or 'generalist' section")

    if root_raw and gen_raw:
        root_agent = _build_agent_profile("root", root_raw, "root_agent")
        generalist = _build_specialist("generalist", gen_raw, "generalist")
    elif root_raw:
        root_agent = _build_agent_profile("root", root_raw, "root_agent")
        generalist = SpecialistConfig(
            name=root_agent.name,
            system_prompt=root_agent.system_prompt,
            description=root_agent.description,
            provider=root_agent.provider,
            base_url=root_agent.base_url,
            model=root_agent.model,
            api_key_env=root_agent.api_key_env,
            temperature=root_agent.temperature,
            max_tokens=root_agent.max_tokens,
            timeout=root_agent.timeout,
            tools=root_agent.tools,
        )
    else:
        assert gen_raw is not None
        generalist = _build_specialist("generalist", gen_raw, "generalist")
        root_agent = AgentProfileConfig(
            name=generalist.name,
            system_prompt=generalist.system_prompt,
            description=generalist.description,
            provider=generalist.provider,
            base_url=generalist.base_url,
            model=generalist.model,
            api_key_env=generalist.api_key_env,
            temperature=generalist.temperature,
            max_tokens=generalist.max_tokens,
            timeout=generalist.timeout,
            tools=generalist.tools,
        )

    agents = {
        name: _build_agent_profile(name, spec, "agent")
        for name, spec in (raw.get("agents") or {}).items()
    }

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
    limits = _build_limits(raw.get("limits"))

    return ConductorConfig(
        root_agent=root_agent,
        agents=agents,
        generalist=generalist,
        specialists=specialists,
        max_hops=max_hops,
        tool_retrieval=tool_retrieval,
        tool_permissions=tool_permissions,
        limits=limits,
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

    if env_config := os.getenv("OJ_CONFIG"):
        config_path = Path(env_config)
        if not config_path.exists():
            raise FileNotFoundError(f"OJ_CONFIG points to non-existent file: {env_config}")
        return _load_single_config(config_path)

    ws = workspace or discover_workspace()
    global_file = ws.global_root / "config.yaml"
    if not global_file.exists():
        global_file = ws.global_root / "config" / "config.yaml"

    local_file: Path | None = None
    if ws.local_root:
        local_file = ws.local_root / "config.yaml"
        if not local_file.exists():
            local_file = ws.local_root / "config" / "config.yaml"

    if global_file.exists() and local_file and local_file.exists():
        global_cfg = _load_single_config(global_file)
        local_cfg = _load_single_config(local_file)
        return merge_configs(global_cfg, local_cfg)

    if local_file and local_file.exists():
        return _load_single_config(local_file)

    if global_file.exists():
        return _load_single_config(global_file)

    p = locate_config()
    return _load_single_config(p)


def get_delegation_mask(specialists: dict[str, SpecialistConfig]) -> dict[str, list[str]]:
    """Build delegation mask from specialist configs."""
    return {name: list(s.delegates_to) for name, s in specialists.items()}
