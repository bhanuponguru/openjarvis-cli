from openjarvis.model_types import SpecialistConfig
from openjarvis.prompts import (
    build_generalist_routing_prompt,
    build_specialist_completion_prompt,
    build_specialist_prompt,
)


def test_build_generalist_routing_prompt_with_descriptions():
    specs = {
        "math": SpecialistConfig(
            name="math",
            system_prompt="You are the math specialist.",
            description="Solves mathematical calculations.",
        ),
        "code": SpecialistConfig(
            name="code",
            system_prompt="You are the code specialist.",
            description="Writes software code.",
        ),
    }
    prompt = build_generalist_routing_prompt(specs)
    assert "### Routing & Dispatch Protocol" in prompt
    assert "- `math`: Solves mathematical calculations." in prompt
    assert "- `code`: Writes software code." in prompt
    assert "[ROUTE: <specialist_name>]" in prompt
    assert "[ROUTE: return]" in prompt


def test_build_generalist_routing_prompt_fallback_description():
    specs = {
        "math": SpecialistConfig(
            name="math",
            system_prompt="\n  Solves algebra and calculus.\nExtra info.",
        ),
    }
    prompt = build_generalist_routing_prompt(specs)
    assert "- `math`: Solves algebra and calculus." in prompt


def test_build_specialist_completion_prompt_with_delegates():
    spec = SpecialistConfig(
        name="math",
        system_prompt="Math expert.",
        delegates_to=["code", "tool_use"],
    )
    prompt = build_specialist_completion_prompt(spec)
    assert "### Delegation & Completion Protocol" in prompt
    assert "[DELEGATE: <specialist_name>]" in prompt
    assert "`code`, `tool_use`" in prompt
    assert "[RETURN]" in prompt


def test_build_specialist_completion_prompt_without_delegates():
    spec = SpecialistConfig(
        name="creative",
        system_prompt="Creative writer.",
        delegates_to=[],
    )
    prompt = build_specialist_completion_prompt(spec)
    assert "### Delegation & Completion Protocol" in prompt
    assert "[DELEGATE:" not in prompt
    assert "[RETURN]" in prompt


def test_build_specialist_prompt_integration():
    generalist = SpecialistConfig(
        name="generalist",
        system_prompt="Primary orchestrator.",
    )
    specialist = SpecialistConfig(
        name="math",
        system_prompt="Math solver.",
        delegates_to=["code"],
    )

    g_prompt = build_specialist_prompt(generalist, available_specialists={"math": specialist}, is_generalist=True)
    assert "Primary orchestrator." in g_prompt
    assert "### Routing & Dispatch Protocol" in g_prompt
    assert "- `math`" in g_prompt

    s_prompt = build_specialist_prompt(specialist, is_generalist=False)
    assert "Math solver." in s_prompt
    assert "### Delegation & Completion Protocol" in s_prompt
    assert "[DELEGATE: <specialist_name>]" in s_prompt
    assert "[RETURN]" in s_prompt
