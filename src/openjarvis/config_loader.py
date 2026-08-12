from dataclasses import fields
from pathlib import Path

import yaml
from yaml import YAMLError

from openjarvis.types import ConductorConfig, SpecialistConfig

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


def load_config(path: str) -> ConductorConfig:
    """Load and validate a YAML config file."""
    p = Path(path)
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
        raise ValueError(f"Error parsing YAML config {path}: {exc}")

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
