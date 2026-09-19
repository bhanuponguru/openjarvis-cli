from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage

from openjarvis.conductor import Conductor
from openjarvis.model_types import (
    ConductorConfig,
    SpecialistConfig,
    ToolRetrievalConfig,
)
from openjarvis.tool_retriever import ToolRetriever
from openjarvis.tools import ToolRegistry


def _create_mock_registry() -> ToolRegistry:
    reg = ToolRegistry()

    @reg.tool()
    def calculate(expr: str) -> str:
        """Evaluate a math expression."""
        return "42"

    @reg.tool()
    def run_code(script: str) -> str:
        """Run a Python script."""
        return "ok"

    @reg.tool()
    def fetch_web(url: str) -> str:
        """Fetch content from the web."""
        return "content"

    return reg


def test_tool_registry_subset():
    reg = _create_mock_registry()
    sub = reg.subset(["calculate", "unknown_tool"])
    tools = sub.get_tools()
    assert "calculate" in tools
    assert "run_code" not in tools
    assert "fetch_web" not in tools
    assert len(tools) == 1


def test_tool_retriever_scoped_allowed_tools():
    reg = _create_mock_registry()
    cfg = ToolRetrievalConfig(enabled=True, always_on_tools=["fetch_web"])
    retriever = ToolRetriever(registry=reg, config=cfg)

    # Retrieval allowed only for calculate
    retrieved = retriever.retrieve("math calculation", allowed_tools=["calculate"])
    names = [t.name for t in retrieved]
    assert names == ["calculate"]
    # fetch_web is always_on in config, but NOT in allowed_tools, so it must be excluded!
    assert "fetch_web" not in names

    # Empty allowed_tools returns empty list
    assert retriever.retrieve("anything", allowed_tools=[]) == []

    # Scoped retrieved registry
    ret_reg = retriever.create_retrieved_registry("math calculation", allowed_tools=["calculate"])
    assert list(ret_reg.get_tools().keys()) == ["calculate"]


def test_conductor_specialist_tool_scoping():
    reg = _create_mock_registry()
    generalist = SpecialistConfig(
        name="generalist",
        system_prompt="Generalist router.",
        base_url="http://test/v1",
        model="test-model",
    )
    math = SpecialistConfig(
        name="math",
        system_prompt="Math solver.",
        base_url="http://test/v1",
        model="test-model",
        tools=["calculate"],  # Only permitted to use calculate
    )
    code = SpecialistConfig(
        name="code",
        system_prompt="Code writer.",
        base_url="http://test/v1",
        model="test-model",
        tools=[],  # Pure reasoning specialist with 0 tools
    )
    cfg = ConductorConfig(generalist=generalist, specialists={"math": math, "code": code})

    mock_model = MagicMock()
    mock_model.bind_tools.return_value = mock_model
    mock_model.invoke.return_value = AIMessage(content="Result [RETURN]")

    with patch.object(Conductor, "_get_chat_model", return_value=mock_model):
        c = Conductor(config=cfg, tools=reg)

        # Call math node
        node_fn = c._make_agent_node("math")
        state = {"messages": [], "hops": 0}
        node_fn(state)

        # Verify bind_tools was called with only calculate
        assert mock_model.bind_tools.called
        bound_tools = mock_model.bind_tools.call_args[0][0]
        assert len(bound_tools) == 1
        assert bound_tools[0]["function"]["name"] == "calculate"

        # Reset mock
        mock_model.bind_tools.reset_mock()

        # Call code node (tools=[])
        code_node_fn = c._make_agent_node("code")
        code_node_fn(state)

        # bind_tools should NOT be called since tools list is empty
        assert not mock_model.bind_tools.called


def test_conductor_blocks_unpermitted_tool_execution():
    reg = _create_mock_registry()
    generalist = SpecialistConfig(
        name="generalist",
        system_prompt="Generalist router.",
        base_url="http://test/v1",
        model="test-model",
    )
    math = SpecialistConfig(
        name="math",
        system_prompt="Math solver.",
        base_url="http://test/v1",
        model="test-model",
        tools=["calculate"],  # Only calculate permitted
    )
    cfg = ConductorConfig(generalist=generalist, specialists={"math": math})

    c = Conductor(config=cfg, tools=reg)

    # State where math attempts to call run_code (which is not permitted for math)
    state = {
        "current_role": "math",
        "last_tool_calls": [
            {
                "id": "call_1",
                "function": {"name": "run_code", "arguments": '{"script": "print(1)"}'},
            }
        ],
        "messages": [],
    }

    new_state = c._tool_execution_node(state)
    messages = new_state["messages"]
    assert len(messages) == 1
    assert "Tool 'run_code' is not permitted for specialist 'math'" in messages[0]["content"]
    assert any("Security blocked unpermitted tool 'run_code'" in ev.get("content", "") for ev in new_state.get("events", []))
