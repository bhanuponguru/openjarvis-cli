from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from openjarvis.conductor import Conductor
from openjarvis.model_types import ConductorConfig, SpecialistConfig
from openjarvis.tools import ToolRegistry


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


def _make_mock_model(responses):
    model = MagicMock()
    if isinstance(responses, list):
        model.invoke.side_effect = [
            AIMessage(content=r) if isinstance(r, str) else r for r in responses
        ]
    else:
        model.invoke.return_value = (
            AIMessage(content=responses) if isinstance(responses, str) else responses
        )
    model.bind_tools.return_value = model
    return model


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
    mock_model = _make_mock_model("Hello there!\n[ROUTE: return]")
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config)
        steps = list(c.chat("Hi"))
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

    mock_model = _make_mock_model(call_responses)
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config)
        steps = list(c.chat("What is 6*7?"))

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

    config.specialists["tool_use"] = SpecialistConfig(
        name="tool_use",
        system_prompt="Tool specialist",
        base_url="http://test/v1",
        model="test-model",
        delegates_to=[],
    )

    mock_model = _make_mock_model(call_responses)
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
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

    mock_model = _make_mock_model(call_responses)
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config)
        steps = list(c.chat("Test"))

        route_events = [s for s in steps if s["type"] == "route"]
        invalid = [r for r in route_events if r.get("from_role") == "math"]
        assert len(invalid) == 1
        assert invalid[0]["from_role"] == "math"
        assert invalid[0]["to_role"] == "generalist"
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
    mock_model = MagicMock()
    mock_model.stream.return_value = [
        AIMessage(content="Hel"),
        AIMessage(content="lo!"),
        AIMessage(content="\n[ROUTE: return]"),
    ]
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config)
        tokens = list(c.chat_stream("Hi"))
        assert "".join(tokens).strip() == "Hello!"
        assert len([t for t in tokens if t]) > 1


def test_tool_result_is_sent_to_followup_llm_call(config):
    """A tool result must be visible to the model call that writes the answer."""
    registry = ToolRegistry()

    @registry.tool()
    def double(n: int) -> int:
        return n * 2

    first = AIMessage(
        content="",
        tool_calls=[{"id": "call_1", "name": "double", "args": {"n": 21}}],
    )
    second = AIMessage(content="The result is 42.\n[ROUTE: return]")

    mock_model = MagicMock()
    mock_model.invoke.side_effect = [first, second]
    mock_model.bind_tools.return_value = mock_model

    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config, tools=registry)
        steps = list(c.chat("Double 21"))

    assert steps[-1]["type"] == "final"
    assert steps[-1]["content"] == "The result is 42."
    assert any(m.get("role") == "tool" and "42" in str(m.get("content")) for m in c.history)


def test_strip_role_echo_removes_prefix(config):
    """_strip_role_echo removes a leading [role]: prefix."""
    c = Conductor(config=config)
    assert c._strip_role_echo("[knowledge]: Some answer") == "Some answer"
    assert c._strip_role_echo("[generalist]: Hello") == "Hello"
    assert c._strip_role_echo("No prefix here") == "No prefix here"
    assert c._strip_role_echo("") == ""


def test_routing_loop_prevention_injects_synthesis_prompt(config):
    """If the generalist tries to re-route to a specialist that already answered,
    a system message should be injected telling it to synthesise instead."""
    call_responses = [
        "Let me ask knowledge.\n[ROUTE: math]",       # Generalist → math
        "The answer is 42.\n[RETURN]",                  # Math returns
        "Let me ask again.\n[ROUTE: math]",             # Generalist tries math AGAIN
        "Here is the answer.\n[ROUTE: return]",         # Generalist forced to synthesise
    ]

    mock_model = _make_mock_model(call_responses)
    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config)
        steps = list(c.chat("What is 6*7?"))

    assert mock_model.invoke.call_count == 4

    sys_msgs = [
        m for m in c.history
        if m["role"] == "system" and "already received an answer" in m.get("content", "")
    ]
    assert len(sys_msgs) == 1

    final_events = [s for s in steps if s["type"] == "final"]
    assert len(final_events) == 1


def test_tool_events_yielded_from_chat(config):
    """tool_call and tool_result events must be yielded from chat() for the CLI to show them."""
    registry = ToolRegistry()

    @registry.tool()
    def double(n: int) -> int:
        return n * 2

    first = AIMessage(
        content="",
        tool_calls=[{"id": "call_tc", "name": "double", "args": {"n": 5}}],
    )
    second = AIMessage(content="Result is 10.\n[ROUTE: return]")

    mock_model = MagicMock()
    mock_model.invoke.side_effect = [first, second]
    mock_model.bind_tools.return_value = mock_model

    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=config, tools=registry)
        steps = list(c.chat("Double 5"))

    tool_call_events = [s for s in steps if s["type"] == "tool_call"]
    tool_result_events = [s for s in steps if s["type"] == "tool_result"]
    assert len(tool_call_events) == 1
    assert tool_call_events[0]["name"] == "double"
    assert len(tool_result_events) == 1
    assert tool_result_events[0]["result"] == "10" or tool_result_events[0]["result"] == 10
