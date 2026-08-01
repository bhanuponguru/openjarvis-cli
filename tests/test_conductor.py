from unittest.mock import patch

import pytest

from openjarvis.conductor import Conductor
from openjarvis.types import ConductorConfig, SpecialistConfig


@pytest.fixture
def config():
    """A ConductorConfig with a generalist and two specialists."""
    generalist = SpecialistConfig(
        name="generalist",
        system_prompt="You are a helpful assistant.",
        base_url="http://test/v1",
        model="test-model",
        temperature=0.7,
    )
    math = SpecialistConfig(
        name="math",
        system_prompt="You are a math expert.",
        base_url="http://test/v1",
        model="test-model",
        temperature=0.3,
        delegates_to=["tool_use"],
    )
    code = SpecialistConfig(
        name="code",
        system_prompt="You are a code expert.",
        base_url="http://test/v1",
        model="test-model",
        temperature=0.2,
        delegates_to=["math"],
    )
    return ConductorConfig(generalist=generalist, specialists={"math": math, "code": code})


def test_conductor_init(config):
    c = Conductor(config=config)
    assert c.config.generalist.name == "generalist"
    assert c.history == []


def test_conductor_loads_from_path(tmp_path):
    """Load from YAML config path."""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text("""
generalist:
  name: "generalist"
  system_prompt: "You are a helpful assistant."
  provider: "openai"
  base_url: "http://test/v1"
  model: "test-model"
specialists: {}
""")
    c = Conductor(config_path=str(config_path))
    assert c.config.generalist.name == "generalist"


def test_chat_direct_return(config):
    """Generalist returns [ROUTE: return] directly."""
    with patch("openjarvis.conductor.call_llm") as mock_call:
        mock_call.return_value = "Hello there!\n[ROUTE: return]"
        c = Conductor(config=config)
        steps = list(c.chat("Hi"))
        # Should yield one step: the final response
        final = steps[-1]
        assert final["type"] == "final"
        assert "Hello there!" in final["content"]


def test_chat_routes_to_specialist(config):
    """Generalist routes to math, specialist returns, generalist synthesises final."""
    call_responses = [
        "Let me calculate that.\n[ROUTE: math]",          # Generalist → math
        "The answer is 42.\n[RETURN]",                     # Math → back to generalist
        "The answer is 42.\n[ROUTE: return]",              # Generalist → final
    ]

    with patch("openjarvis.conductor.call_llm") as mock_call:
        mock_call.side_effect = call_responses
        c = Conductor(config=config)
        steps = list(c.chat("What is 6*7?"))

        # Should yield: route(generalist→math), route(math→generalist), final
        route_events = [s for s in steps if s["type"] == "route"]
        final = [s for s in steps if s["type"] == "final"]

        assert len(route_events) >= 2
        assert route_events[0]["from_role"] == "generalist"
        assert route_events[0]["to_role"] == "math"
        assert route_events[1]["from_role"] == "math"
        assert route_events[1]["to_role"] == "generalist"
        assert len(final) == 1
        assert "The answer is 42." in final[0]["content"]


def test_chat_multi_hop_delegation(config):
    """Generalist → math → tool_use → generalist → return (through delegation chain)."""
    call_responses = [
        "Routing to math.\n[ROUTE: math]",                    # Generalist
        "I need the tool.\n[DELEGATE: tool_use]",              # Math → tool_use
        "Tool result is 99.\n[RETURN]",                        # tool_use → back to generalist
        "Result is 99.\n[ROUTE: return]",                      # Generalist → final
    ]

    # Need tool_use in config
    config.specialists["tool_use"] = SpecialistConfig(
        name="tool_use",
        system_prompt="Tool specialist",
        base_url="http://test/v1",
        model="test-model",
        delegates_to=[],
    )

    with patch("openjarvis.conductor.call_llm") as mock_call:
        mock_call.side_effect = call_responses
        c = Conductor(config=config)
        steps = list(c.chat("Compute something"))

        route_events = [s for s in steps if s["type"] == "route"]
        assert any(r["from_role"] == "generalist" and r["to_role"] == "math" for r in route_events)
        assert any(r["from_role"] == "math" and r["to_role"] == "tool_use" for r in route_events)


def test_invalid_delegation_returns_to_generalist(config):
    """If specialist tries invalid delegation, conductor intercepts."""
    call_responses = [
        "Routing.\n[ROUTE: math]",
        "I delegate to nowhere.\n[DELEGATE: nonexistent]",  # invalid
        "I see the delegation failed. Let me answer directly.\n[ROUTE: return]",  # generalist recovery
    ]

    with patch("openjarvis.conductor.call_llm") as mock_call:
        mock_call.side_effect = call_responses
        c = Conductor(config=config)
        steps = list(c.chat("Test"))

        # Should have route event showing the invalid delegation
        route_events = [s for s in steps if s["type"] == "route"]
        invalid = [r for r in route_events if r.get("from_role") == "math"]
        # After invalid delegation, the system message is injected and generalist recovers
        assert len(invalid) == 1
        assert invalid[0]["from_role"] == "math"
        assert invalid[0]["to_role"] == "generalist"
        # The generalist produces a real final answer — exercises the actual recovery path
        assert len(steps) > 0
        last_step = steps[-1]
        assert last_step["type"] == "final"
        assert "I see the delegation failed" in last_step["content"]


def test_save_and_load_history(config, tmp_path):
    """Conversation history persist/restore."""
    c = Conductor(config=config)
    c.history = [
        {"role": "user", "content": "hello"},
        {"role": "generalist", "content": "hi", "route": "return"},
    ]
    path = tmp_path / "history.json"
    c.save_history(str(path))
    assert path.exists()

    c2 = Conductor(config=config)
    c2.load_history(str(path))
    assert len(c2.history) == 2
    assert c2.history[0]["content"] == "hello"


def test_chat_stream_yields_content(config):
    """chat_stream streams the generalist's own deltas, tag suppressed."""
    with patch("openjarvis.conductor.call_llm_stream") as mock_stream:
        mock_stream.return_value = iter(["Hel", "lo!", "\n[ROUTE: return]"])
        c = Conductor(config=config)
        tokens = list(c.chat_stream("Hi"))
        assert "".join(tokens).strip() == "Hello!"
        # It is a real stream, not one buffered string replayed.
        assert len([t for t in tokens if t]) > 1
