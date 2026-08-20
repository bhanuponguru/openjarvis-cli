import os
from dataclasses import fields
from pathlib import Path

import yaml
from yaml import YAMLError

from openjarvis.model_types import ConductorConfig, SpecialistConfig

# Valid top-level keys for a `SpecialistConfig` dataclass
_VALID_KEYS = {f.name for f in fields(SpecialistConfig)}


def _build_specialist(name: str, spec: dict, section: str) -> SpecialistConfig:
    """Construct a SpecialistConfig, reporting unknown keys clearly.

    `SpecialistConfig(**spec)` alone raises a bare TypeError naming only the
    first bad key, with no hint of which config section it came from or what
    the valid keys are -- unhelpful when a typo sits 200 lines into a YAML file.
    """
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


def locate_config() -> Path:
    """Locate config file in standard search locations.

    Search order:
    1. OJ_CONFIG environment variable (highest priority)
    2. Current directory: ./specialists.yaml
    3. User config: ~/.config/openjarvis/specialists.yaml
    4. System config: /etc/openjarvis/specialists.yaml (Linux/macOS only)

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

    # 2. Current directory
    cwd_config = Path.cwd() / "specialists.yaml"
    if cwd_config.exists():
        return cwd_config

    # 3. User config directory (~/.config/openjarvis/)
    user_config = Path.home() / ".config" / "openjarvis" / "specialists.yaml"
    if user_config.exists():
        return user_config

    # 4. System config (Linux/macOS only)
    if os.name != "nt":
        system_config = Path("/etc/openjarvis/specialists.yaml")
        if system_config.exists():
            return system_config

    # Config not found — build a helpful message listing all searched paths
    searched = [
        "  1. OJ_CONFIG environment variable (not set)",
        f"  2. {cwd_config}",
        f"  3. {user_config}",
    ]
    if os.name != "nt":
        searched.append(f"  4. {system_config}")
    searched_str = "\n".join(searched)
    raise FileNotFoundError(
        f"specialists.yaml not found!\n\nSearched locations:\n{searched_str}\n\n"
        "Run 'openjarvis' to launch the setup wizard, or set OJ_CONFIG=/path/to/config.yaml"
    )


def load_config(path: str | None = None) -> ConductorConfig:
    """Load and validate a YAML config file.

    Args:
        path: Path to config file. If None, searches standard locations.

    Returns:
        ConductorConfig object.

    Raises:
        FileNotFoundError: If config file not found.
        ValueError: If config file is invalid.
    """
    p = locate_config() if path is None else Path(path)

    try:
        text = p.read_text()
    except FileNotFoundError:
        # Preserve the original behaviour expected by callers/tests: raise
        # FileNotFoundError so external code can catch it specifically.
        raise

    try:
        raw = yaml.safe_load(text)
    except YAMLError as exc:
        # Include the path to help users find the broken file quickly
        raise ValueError(f"Error parsing YAML config {path}: {exc}") from exc

    if raw is None:
        raise ValueError(f"Config file {path!r} is empty or contains no YAML document")

    if "generalist" not in raw:
        raise ValueError("Config must have a 'generalist' section")

    generalist = _build_specialist("generalist", raw["generalist"], "generalist")

    specialists = {
        name: _build_specialist(name, spec, "specialist")
        for name, spec in (raw.get("specialists") or {}).items()
    }

    # Catch delegation typos at load time. Left unvalidated, a bad target only
    # surfaces mid-conversation as a routing error the user pays tokens for.
    for name, spec in specialists.items():
        for target in spec.delegates_to:
            # Allow delegation to the generalist by name; otherwise the target
            # must be a defined specialist. Provide a clear diagnostic on errors.
            if target != "generalist" and target not in specialists:
                raise ValueError(
                    f"specialist '{name}' delegates to '{target}', which is not "
                    f"defined. Known specialists: {', '.join(sorted(specialists))}, generalist"
                )

    max_hops = raw.get("max_hops", ConductorConfig.max_hops)
    if not isinstance(max_hops, int) or isinstance(max_hops, bool) or max_hops < 1:
        raise ValueError(f"max_hops must be a positive integer, got {max_hops!r}")

    return ConductorConfig(
        generalist=generalist, specialists=specialists, max_hops=max_hops
    )


def get_delegation_mask(specialists: dict[str, SpecialistConfig]) -> dict[str, list[str]]:
    """Build delegation mask from specialist configs."""
    return {name: list(s.delegates_to) for name, s in specialists.items()}
