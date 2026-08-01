from openjarvis.types import ConductorConfig, SpecialistConfig


def test_specialist_config():
    cfg = SpecialistConfig(
        name="math",
        system_prompt="You are a math expert",
        base_url="http://localhost:11434/v1",
        model="llama3",
        delegates_to=["tool_use"],
    )
    assert cfg.name == "math"
    assert "tool_use" in cfg.delegates_to


def test_specialist_config_defaults():
    cfg = SpecialistConfig(name="test", system_prompt="test", base_url="http://localhost:11434/v1")
    assert cfg.provider == "openai"
    assert cfg.temperature == 0.7
    assert cfg.delegates_to == []
    assert cfg.max_tokens is None
    assert cfg.timeout == 60.0


def test_conductor_config():
    generalist = SpecialistConfig(name="generalist", system_prompt="you are jarvis", base_url="http://localhost:11434/v1")
    math = SpecialistConfig(name="math", system_prompt="math expert", base_url="http://localhost:11434/v1")
    config = ConductorConfig(generalist=generalist, specialists={"math": math})
    assert config.generalist.name == "generalist"
    assert config.specialists["math"].name == "math"


def test_conductor_config_has_hop_cap_by_default():
    """Loop safety must be on without opt-in -- a spin costs real money."""
    generalist = SpecialistConfig(name="generalist", system_prompt="x")
    assert ConductorConfig(generalist=generalist).max_hops == 10
