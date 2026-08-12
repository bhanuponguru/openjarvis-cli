"""Tests for the tool calling system."""
from __future__ import annotations

from unittest.mock import MagicMock

from openjarvis.tools import (
    DEFAULT_REGISTRY,
    ToolRegistry,
    _json_serializable,
    _python_type_to_json,
)


class TestPythonTypeToJson:
    def test_primitives(self) -> None:
        assert _python_type_to_json(str) == "string"
        assert _python_type_to_json(int) == "integer"
        assert _python_type_to_json(float) == "number"
        assert _python_type_to_json(bool) == "boolean"


class TestJsonSerializable:
    def test_primitives(self) -> None:
        assert _json_serializable("hello") == "hello"
        assert _json_serializable(42) == 42
        assert _json_serializable(3.14) == 3.14


class TestToolRegistryOpenAIFormat:
    def test_empty(self) -> None:
        assert ToolRegistry().to_openai_format() == []

    def test_single_tool(self) -> None:
        fresh = ToolRegistry()

        @fresh.tool()
        def get_weather(city: str) -> str:
            """Get weather for a city."""
            return "sunny"

        tools = fresh.to_openai_format()
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "get_weather"


class TestToolRegistryExecute:
    def test_known_tool(self) -> None:
        fresh = ToolRegistry()

        @fresh.tool()
        def double(n: int) -> int:
            return n * 2

        result = fresh.execute({"name": "double", "arguments": {"n": 21}})
        assert result == 42

    def test_unknown_tool(self) -> None:
        fresh = ToolRegistry()
        result = fresh.execute({"name": "missing", "arguments": {}})
        assert "error" in result


class TestToolRegistryParseToolCalls:
    def test_empty(self) -> None:
        fresh = ToolRegistry()
        mock_ = MagicMock()
        mock_.tool_calls = []
        assert fresh.parse_tool_calls(mock_) == []

    def test_single_call(self) -> None:
        fresh = ToolRegistry()
        func = MagicMock()
        func.name = "weather"
        func.arguments = '{"city": "Berlin"}'
        tc = MagicMock()
        tc.id = "call_abc"
        tc.function = func
        mock_ = MagicMock()
        mock_.tool_calls = [tc]
        result = fresh.parse_tool_calls(mock_)
        assert len(result) == 1
        assert result[0]["name"] == "weather"


class TestModuleLevelGlobals:
    def test_default_registry_exists(self) -> None:
        assert DEFAULT_REGISTRY is not None
        assert isinstance(DEFAULT_REGISTRY, ToolRegistry)
