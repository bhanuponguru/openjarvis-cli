"""Interactive CLI for the OpenJarvis Conductor."""

import sys

from rich.console import Console
from rich.markdown import Markdown

from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.config_loader import load_config


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments (unused, reserved for future
              expansion). The config path is searched in standard locations
              or via OJ_CONFIG environment variable.
    """
    # Create Console fresh each call so test frameworks that patch sys.stdout
    # (e.g. capsys) capture the output correctly.
    console = Console()

    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as exc:
        Console(stderr=True).print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    tools = create_builtin_registry()
    conductor = Conductor(config=config, tools=tools)

    console.print("[bold]OpenJarvis[/bold] — type [dim]exit[/dim] or [dim]quit[/dim] to stop\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if user_input.lower() in ("exit", "quit"):
            break

        if not user_input:
            continue

        for event in conductor.chat(user_input):
            etype = event.get("type")

            if etype == "route":
                console.print(
                    f"  [dim]↳ routing: {event['from_role']} → {event['to_role']}[/dim]"
                )

            elif etype == "intermediate":
                content = (event.get("content") or "").strip()
                if content:
                    console.print(
                        f"  [dim italic][{event['role']}][/dim italic] {content[:300]}"
                    )

            elif etype == "tool_call":
                console.print(
                    f"  [cyan]⚙ tool:[/cyan] [bold]{event.get('name', '?')}[/bold]"
                )

            elif etype == "tool_result":
                result_str = str(event.get("result", ""))
                preview = result_str[:120] + ("…" if len(result_str) > 120 else "")
                console.print(f"  [dim]  → {preview}[/dim]")

            elif etype == "final":
                content = (event.get("content") or "").strip()
                if content:
                    console.print()
                    console.print(Markdown(content))
                    console.print()

            elif etype == "error":
                console.print(f"  [red]⚠ {event.get('content', 'unknown error')}[/red]")
