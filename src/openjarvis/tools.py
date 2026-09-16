"""Tool calling system for OpenJarvis.

Tools are registered via the :func:`tool` decorator and stored in a
:class:`ToolRegistry`.  The registry can export tools in OpenAI SDK format and
execute tool calls returned by the model.

Example::

    from openjarvis.tools import tool, ToolRegistry

    registry = ToolRegistry()

    @registry.tool()
    def get_weather(city: str) -> str:
        \"\"\"Get the current weather in a city.\"\"\"
        return f"The weather in {city} is sunny."

    # Export to OpenAI format
    openai_tools = registry.to_openai_format()

    # Execute a tool call from the model
    result = registry.execute(tool_call)
"""
from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, get_type_hints

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ToolParameter:
    """A parameter accepted by a tool function."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class Tool:
    """A callable tool with OpenAI-compatible metadata.

    Attributes:
        name: Unique identifier for the tool. Matches the Python function name.
        description: Human-readable description (taken from the function's
            docstring; the first line is the summary, remaining lines are the
            description body).
        parameters: JSON Schema describing the tool's parameters.
        func: The underlying Python callable.
    """

    name: str
    description: str
    parameters: dict
    func: Callable[..., Any]
    _original: Callable[..., Any] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self._original is None:
            self._original = self.func


@dataclass
class ToolRegistry:
    """Global registry for all available tools.

    Tools are registered by applying an instance of this class as a decorator
    to a function.  The decorator returns the function unchanged, so the tool
    is available both as a callable and through the registry.
    """

    _tools: dict[str, Tool] = field(default_factory=dict)

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> Callable[[F], F]:
        """Decorator that registers ``func`` as a tool.

        Args:
            name: Override the tool name.  Defaults to the function's ``__name__``.
            description: Override the tool description.  Defaults to the
                function's docstring (first line = summary; rest = description).

        Returns:
            A decorator that registers the function and returns it unchanged.

        Example::

            @registry.tool()
            def my_tool(arg1: str, arg2: int) -> str:
                \"\"\"Short summary.\n\n                Longer description.\"\"\"
                ...
        """

        def decorator(func: F) -> F:
            tool_name = name or func.__name__

            # Extract description from docstring
            raw_doc = inspect.getdoc(func) or ""
            lines = raw_doc.splitlines()
            summary = lines[0].strip() if lines else ""
            doc_body = "\n".join(line.strip() for line in lines[1:]).strip()
            full_desc = summary + ("\n\n" + doc_body if doc_body else "")

            tool_desc = description or full_desc or f"Tool: {tool_name}"

            # Build JSON Schema from type hints
            try:
                type_hints = get_type_hints(func)
            except Exception:
                # Fall back to inspect.Signature if get_type_hints fails
                type_hints = {}

            sig = inspect.signature(func)
            properties: dict = {}
            required: list[str] = []

            for param_name, param in sig.parameters.items():
                json_type = _python_type_to_json(type_hints.get(param_name, param.annotation))
                param_doc = ""
                if raw_doc:
                    # Try to extract per-parameter documentation from docstring
                    param_doc = _get_param_description(raw_doc, param_name)

                if param.default is inspect.Parameter.empty:
                    required.append(param_name)
                    properties[param_name] = {
                        "type": json_type,
                        "description": param_doc or f"Parameter {param_name}",
                    }
                else:
                    properties[param_name] = {
                        "type": json_type,
                        "description": param_doc or f"Parameter {param_name}",
                        "default": _json_serializable(param.default),
                    }

            parameters_schema: dict = {
                "type": "object",
                "properties": properties,
            }
            if required:
                parameters_schema["required"] = required

            tool_obj = Tool(
                name=tool_name,
                description=tool_desc,
                parameters=parameters_schema,
                func=func,
            )
            self._tools[tool_name] = tool_obj
            return func

        return decorator

    # Provide shorthand so ``@registry.tool()`` works directly
    __call__ = tool

    def to_openai_format(self) -> list[dict]:
        """Return tools serialised to the ``tools`` value expected by the OpenAI SDK.

        Example::

            tools = registry.to_openai_format()
            completion = client.chat.completions.create(
                model="...",
                messages=[...],
                tools=tools,
            )
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]

    def get(self, name: str) -> Tool | None:
        """Return the tool with the given name, or ``None`` if not found."""
        return self._tools.get(name)

    def register(self, tool_obj: Tool) -> None:
        """Register an existing Tool object directly."""
        self._tools[tool_obj.name] = tool_obj

    def add_tool(
        self,
        func: Callable[..., Any],
        name: str | None = None,
        description: str | None = None,
    ) -> Tool:
        """Register a callable directly as a tool and return the created Tool object."""
        decorator = self.tool(name=name, description=description)
        decorator(func)
        registered_name = name or func.__name__
        return self._tools[registered_name]

    def get_tools(self) -> dict[str, Tool]:
        """Return a copy of all registered tools mapping name -> Tool."""
        return dict(self._tools)

    def execute(self, tool_call: dict) -> Any:
        """Execute a single tool call and return its result.

        Args:
            tool_call: A dict with at least ``{"name": ..., "arguments": ...}``.
                ``arguments`` may be a JSON string or already-parsed dict.

        Returns:
            The return value of the tool function, serialised to a JSON-compatible
            type so it can be embedded in a ``tool`` role message.

        Raises:
            KeyError: If the tool name is not registered.
            TypeError: If arguments don't match the signature.
        """
        name = tool_call.get("name") or tool_call.get("function", {}).get("name", "")
        args_raw = tool_call.get("arguments") or tool_call.get("function", {}).get("arguments", "{}")

        if isinstance(args_raw, str):
            try:
                args: dict = json.loads(args_raw)
            except json.JSONDecodeError as exc:
                return {"error": f"Invalid JSON arguments: {exc}"}
        else:
            # Ensure we end up with a plain dict; if the provided value is
            # not mapping-like, return a clear error instead of raising later.
            if isinstance(args_raw, dict):
                args = dict(args_raw)
            else:
                return {"error": f"Arguments must be an object/dict, got {type(args_raw).__name__}"}

        tool_obj = self._tools.get(name)
        if tool_obj is None:
            return {"error": f"Unknown tool: {name}"}

        try:
            result = tool_obj.func(**args)
        except TypeError as exc:
            return {"error": f"Argument mismatch for '{name}': {exc}"}
        except Exception as exc:
            return {"error": f"Tool '{name}' raised: {exc}"}

        # Coerce result to a JSON-serialisable type
        if result is None:
            return "OK"
        if isinstance(result, (str, int, float, bool)):
            return result
        try:
            return json.loads(json.dumps(result))
        except Exception:
            return str(result)

    def parse_tool_calls(self, completion: Any) -> list[dict]:
        """Extract tool calls from an OpenAI SDK completion object.

        Handles both ``chat.completions.create`` (returns
        ``CompletionMessage.tool_calls``) and the delta objects produced by
        streaming.

        Returns a list of tool-call dicts with keys:
        ``name``, ``arguments`` (as a dict), ``id``.

        If there are no tool calls, returns an empty list.
        """
        tool_calls: list = getattr(completion, "tool_calls", None) or []

        parsed = []
        for tc in tool_calls:
            func = getattr(tc, "function", None) or {}
            raw_args = getattr(func, "arguments", "{}")
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
            else:
                args = dict(raw_args) if raw_args else {}

            parsed.append(
                {
                    "id": getattr(tc, "id", ""),
                    "name": getattr(func, "name", ""),
                    "arguments": args,
                }
            )
        return parsed


# --------------------------------------------------------------------------
# Module-level convenience registry and decorator
# --------------------------------------------------------------------------


#: The shared global tool registry.  Import this in your app and decorate
#: functions with ``@DEFAULT_REGISTRY.tool()`` for a decorator-less approach.
DEFAULT_REGISTRY = ToolRegistry()

#: Shorthand decorator for the global registry.
tool = DEFAULT_REGISTRY.tool


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


_PYTHON_TYPE_TO_JSON = {
    type(None): "null",
    bool: "boolean",
    int: "integer",
    float: "number",
    str: "string",
    list: "array",
    dict: "object",
    tuple: "array",
    set: "array",
}


def _python_type_to_json(annotation: Any) -> str:
    """Map a Python type (or ``typing`` alias) to a JSON Schema type string."""
    # Unwrap Union, Optional, etc.
    origin = getattr(annotation, "__origin__", None)
    if origin is list or annotation is list:
        return "array"
    if origin is dict or annotation is dict:
        return "object"
    if origin in (tuple, set) or annotation in (tuple, set):
        return "array"
    if origin is set:
        return "array"

    # Handle typing.Optional / typing.Union[..., None]
    if origin is type(None):
        return "null"
    if origin is not None:
        args = getattr(annotation, "__args__", ())
        non_null = [a for a in args if a is not type(None)]
        if len(non_null) == 1:
            return _python_type_to_json(non_null[0])
        if set(non_null) == {int, float}:
            return "number"

    # Try direct lookup
    for py_type, json_type in _PYTHON_TYPE_TO_JSON.items():
        if annotation is py_type or (inspect.isclass(annotation) and issubclass(annotation, py_type)):
            return json_type

    # Fallback: treat as string
    return "string"


def _json_serializable(value: Any) -> Any:
    """Coerce a Python value to something JSON-serialisable."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_serializable(v) for v in value]
    if isinstance(value, dict):
        return {k: _json_serializable(v) for k, v in value.items()}
    return str(value)


def _get_param_description(doc: str, param_name: str) -> str:
    """Try to extract per-parameter documentation from a docstring.

    Handles both ``Args:`` sections (Sphinx / NumPy style) and
    ``Parameters:`` sections.

    Returns an empty string if no description is found.
    """
    import re

    pattern = rf"^\s*{re.escape(param_name)}\s*:\s*[^\n]+\n(\s{2,}.+?)(?=^\s*\w|\Z)"
    match = re.search(pattern, doc, re.MULTILINE | re.DOTALL)
    if match:
        lines = match.group(1).strip().splitlines()
        return " ".join(line.strip() for line in lines)
    return ""
