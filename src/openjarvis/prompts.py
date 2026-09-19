"""System prompt templating and routing protocol injection for OpenJarvis specialists."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openjarvis.model_types import SpecialistConfig


def build_generalist_routing_prompt(
    specialists: dict[str, SpecialistConfig] | list[str],
) -> str:
    """Build standardized routing instructions for the generalist router.

    Dynamically lists all declared specialists and instructs the model on
    the exact [ROUTE: <target>] and [ROUTE: return] protocol.
    """
    lines: list[str] = [
        "### Routing & Dispatch Protocol",
        "You are the orchestrator and router. Your job is to analyze the user message, "
        "determine whether specialized domain expertise is required, and either route to "
        "the single most appropriate specialist or answer directly.",
    ]

    if specialists:
        lines.append("\nAvailable Specialists for Delegation:")
        if isinstance(specialists, dict):
            for name, spec in sorted(specialists.items()):
                desc = spec.description
                if not desc and spec.system_prompt:
                    # Take the first non-empty line of the system prompt
                    first_line = next(
                        (line.strip() for line in spec.system_prompt.splitlines() if line.strip()),
                        "",
                    )
                    if first_line:
                        desc = first_line
                desc_str = f": {desc}" if desc else ""
                lines.append(f"- `{name}`{desc_str}")
        else:
            for name in sorted(specialists):
                lines.append(f"- `{name}`")

    lines.extend([
        "\nResponse & Routing Rules:",
        "1. If delegating to a specialist, keep your response minimal and terminate with exactly ONE routing tag on its own line:",
        "   `[ROUTE: <specialist_name>]`",
        "   Do not solve or execute the specialized domain task yourself when a dedicated specialist is available.",
        "2. If the user request is a general greeting, casual remark, basic pleasantry, or if you are presenting the final synthesized response after specialists have returned, terminate with:",
        "   `[ROUTE: return]`",
        "3. Never output multiple routing tags. The routing tag MUST appear on its own line at the very end of your response.",
    ])

    return "\n".join(lines)


def build_specialist_completion_prompt(
    spec: SpecialistConfig,
) -> str:
    """Build standardized delegation and completion instructions for a specialist.

    Instructs the specialist on how to delegate to allowed targets using
    [DELEGATE: <target>] or return results to the conductor via [RETURN].
    """
    lines: list[str] = [
        "### Delegation & Completion Protocol",
    ]

    if spec.delegates_to:
        allowed = ", ".join(f"`{d}`" for d in sorted(spec.delegates_to))
        lines.extend([
            "Subtask Delegation:",
            "- If a subtask strictly requires another specialist's domain expertise, end your response with:",
            "  `[DELEGATE: <specialist_name>]`",
            f"  Permitted delegation targets: {allowed}",
            "- Do not attempt to delegate to any specialist not in the permitted list.",
        ])

    lines.extend([
        "Task Completion:",
        "- When you have completed your analysis/task (or if no delegation is needed), end your response with exactly ONE tag on its own line:",
        "  `[RETURN]`",
        "- The tag MUST appear on its own line at the very end of your response.",
    ])

    return "\n".join(lines)


def build_specialist_prompt(
    spec: SpecialistConfig,
    available_specialists: dict[str, SpecialistConfig] | list[str] | None = None,
    is_generalist: bool = False,
) -> str:
    """Combine base functional system prompt with harness routing/completion templates.

    Args:
        spec: The specialist configuration containing domain instructions.
        available_specialists: Dict or list of available specialists (used for generalist routing).
        is_generalist: True if building prompt for the generalist router.

    Returns:
        The complete, templated system prompt string.
    """
    base_prompt = (spec.system_prompt or "").strip()

    if is_generalist:
        routing_template = build_generalist_routing_prompt(available_specialists or {})
    else:
        routing_template = build_specialist_completion_prompt(spec)

    if not base_prompt:
        return routing_template

    return f"{base_prompt}\n\n{routing_template}"
