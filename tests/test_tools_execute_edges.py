from openjarvis.tools import ToolRegistry


def test_execute_with_json_string_args():
    registry = ToolRegistry()

    @registry.tool()
    def echo(msg: str) -> str:
        return msg

    res = registry.execute({"name": "echo", "arguments": '{"msg": "hello"}'})
    assert res == "hello"


def test_execute_with_dict_args():
    registry = ToolRegistry()

    @registry.tool()
    def add(x: int, y: int) -> int:
        return x + y

    res = registry.execute({"name": "add", "arguments": {"x": 2, "y": 3}})
    assert res == 5


def test_execute_with_malformed_json_returns_error():
    registry = ToolRegistry()

    @registry.tool()
    def noop() -> str:
        return "ok"

    res = registry.execute({"name": "noop", "arguments": '{bad json'})
    assert isinstance(res, dict) and "Invalid JSON" in res.get("error", "")


def test_execute_with_non_dict_args_returns_error():
    registry = ToolRegistry()

    @registry.tool()
    def noop() -> str:
        return "ok"

    res = registry.execute({"name": "noop", "arguments": [1, 2, 3]})
    assert isinstance(res, dict) and "Arguments must be an object/dict" in res.get("error", "")
