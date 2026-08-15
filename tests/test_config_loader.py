import tempfile
from pathlib import Path

import pytest

from openjarvis.config_loader import get_delegation_mask, load_config
from openjarvis.model_types import ConductorConfig, SpecialistConfig

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_config_returns_conductor_config():
    config = load_config(str(FIXTURES / "test_config.yaml"))
    assert isinstance(config, ConductorConfig)
    assert config.generalist.name == "generalist"
    assert "math" in config.specialists
    assert "code" in config.specialists
    assert config.specialists["math"].delegates_to == ["tool_use"]


def test_load_config_all_specialists_present():
    config = load_config(str(FIXTURES / "test_config.yaml"))
    expected = {"math", "code", "tool_use"}
    assert set(config.specialists.keys()) == expected


def test_load_config_rejects_dangling_delegation_target(tmp_path):
    """A delegation typo must fail at load, not mid-conversation.

    Left unvalidated it costs the user real tokens before surfacing as a
    routing error -- and this fixture file itself carried exactly that bug.
    """
    path = tmp_path / "bad.yaml"
    path.write_text(
        "generalist:\n"
        "  system_prompt: g\n"
        "specialists:\n"
        "  math:\n"
        "    system_prompt: m\n"
        "    delegates_to: [tool_use]\n"
    )
    with pytest.raises(ValueError, match="tool_use"):
        load_config(str(path))


def test_load_config_rejects_unknown_key(tmp_path):
    """A typo'd key must name itself, not raise a bare TypeError."""
    path = tmp_path / "typo.yaml"
    path.write_text("generalist:\n  system_prompt: g\n  temperatur: 0.5\n")
    with pytest.raises(ValueError, match="temperatur"):
        load_config(str(path))


def test_load_config_reads_max_hops(tmp_path):
    path = tmp_path / "hops.yaml"
    path.write_text("max_hops: 3\ngeneralist:\n  system_prompt: g\n")
    assert load_config(str(path)).max_hops == 3


def test_load_config_rejects_bad_max_hops(tmp_path):
    path = tmp_path / "hops.yaml"
    path.write_text("max_hops: 0\ngeneralist:\n  system_prompt: g\n")
    with pytest.raises(ValueError, match="max_hops"):
        load_config(str(path))


def test_load_config_defaults_name_from_key(tmp_path):
    """Omitting `name:` should inherit the YAML key rather than fail."""
    path = tmp_path / "noname.yaml"
    path.write_text("generalist:\n  system_prompt: g\nspecialists:\n  math:\n    system_prompt: m\n")
    assert load_config(str(path)).specialists["math"].name == "math"


def test_get_delegation_mask():
    specialists = {
        "math": SpecialistConfig(name="math", system_prompt="", base_url="http://localhost:11434/v1", delegates_to=["tool_use"]),
        "tool_use": SpecialistConfig(name="tool_use", system_prompt="", base_url="http://localhost:11434/v1"),
    }
    mask = get_delegation_mask(specialists)
    assert mask["math"] == ["tool_use"]
    assert mask["tool_use"] == []


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path.yaml")


def test_load_config_rejects_empty_file(tmp_path):
    path = tmp_path / "empty.yaml"
    path.write_text("")
    with pytest.raises(ValueError, match="empty"):
        load_config(str(path))


def test_load_config_missing_generalist():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("specialists:\n  math:\n    name: math\n    system_prompt: test\n    base_url: http://localhost:11434/v1\n")
        path = f.name
    with pytest.raises(ValueError, match="generalist"):
        load_config(path)
