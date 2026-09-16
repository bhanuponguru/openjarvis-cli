"""Built-in tools for OpenJarvis agents.

This module provides a pre-configured registry of tools that agents can use:
- datetime_tools: Date/time manipulation and formatting
- math_tools: Calculations, unit conversions, equation solving
- file_tools: File I/O and directory operations
- web_tools: URL fetching, web search, Wikipedia lookups
- code_tools: Python execution, shell commands, linting
- data_tools: JSON/CSV parsing, regex operations
- memory_tools: Session-scoped note storage
"""

from openjarvis.tools import DEFAULT_REGISTRY, ToolRegistry


def create_builtin_registry(
    *,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
) -> ToolRegistry:
    """Create a tool registry with built-in tools.

    Args:
        include: Whitelist of module names to include (e.g., {"datetime_tools", "math_tools"}).
                 If None, includes all modules except excluded ones.
        exclude: Blacklist of module names to exclude (e.g., {"code_tools"}).
                 If None, includes all modules.

    Returns:
        Populated ToolRegistry ready to pass to Conductor(tools=...).

    Example:
        registry = create_builtin_registry()
        conductor = Conductor(tools=registry)

        registry_safe = create_builtin_registry(exclude={"code_tools"})
        # ^-- safer: no shell or Python execution
    """
    registry = ToolRegistry()

    all_modules = {
        "datetime_tools",
        "math_tools",
        "file_tools",
        "web_tools",
        "code_tools",
        "data_tools",
        "memory_tools",
        "editor_tools",
    }

    modules_to_load = include & all_modules if include is not None else all_modules

    if exclude is not None:
        modules_to_load = modules_to_load - exclude

    _load_tools_into_registry = {
        "datetime_tools": _load_datetime_tools,
        "math_tools": _load_math_tools,
        "file_tools": _load_file_tools,
        "web_tools": _load_web_tools,
        "code_tools": _load_code_tools,
        "data_tools": _load_data_tools,
        "memory_tools": _load_memory_tools,
        "editor_tools": _load_editor_tools,
    }

    for module_name in modules_to_load:
        if module_name in _load_tools_into_registry:
            _load_tools_into_registry[module_name](registry)

    return registry


def _load_datetime_tools(registry: ToolRegistry):
    from . import datetime_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == datetime_tools.__name__:
            registry._tools[name] = tool_obj

def _load_math_tools(registry: ToolRegistry):
    from . import math_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == math_tools.__name__:
            registry._tools[name] = tool_obj

def _load_file_tools(registry: ToolRegistry):
    from . import file_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == file_tools.__name__:
            registry._tools[name] = tool_obj

def _load_web_tools(registry: ToolRegistry):
    from . import web_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == web_tools.__name__:
            registry._tools[name] = tool_obj

def _load_code_tools(registry: ToolRegistry):
    from . import code_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == code_tools.__name__:
            registry._tools[name] = tool_obj

def _load_data_tools(registry: ToolRegistry):
    from . import data_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == data_tools.__name__:
            registry._tools[name] = tool_obj

def _load_memory_tools(registry: ToolRegistry):
    from . import memory_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == memory_tools.__name__:
            registry._tools[name] = tool_obj

def _load_editor_tools(registry: ToolRegistry):
    from . import editor_tools
    for name, tool_obj in DEFAULT_REGISTRY._tools.items():
        if tool_obj.func.__module__ == editor_tools.__name__:
            registry._tools[name] = tool_obj


__all__ = ["create_builtin_registry"]
