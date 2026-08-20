"""Terminal UI for the OpenJarvis REPL using prompt_toolkit + Rich."""

from __future__ import annotations

from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown

from openjarvis.conductor import Conductor

_COMMANDS = ["/exit", "/quit", "/clear", "/help"]
_HISTORY_PATH = Path.home() / ".config" / "openjarvis" / "history.txt"


def create_session() -> PromptSession:
    """Create a prompt_toolkit session with history and command completion."""
    _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    return PromptSession(
        history=FileHistory(str(_HISTORY_PATH)),
        completer=WordCompleter(_COMMANDS, sentence=True),
        enable_history_search=True,
    )


def render_event(console: Console, event: dict) -> None:
    """Render a single Conductor event to the console."""
    etype = event.get("type")

    if etype == "route":
        console.print(
            f"  [dim]↳ routing: {event['from_role']} → {event['to_role']}[/dim]"
        )

    elif etype == "intermediate":
        content = (event.get("content") or "").strip()
        if content:
            role = event["role"]
            console.print(f"  [dim italic]\\[{role}][/dim italic] {content[:300]}")

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


def run_repl(conductor: Conductor, console: Console) -> None:
    """Run the interactive REPL using prompt_toolkit input and Rich output."""
    session = create_session()
    console.print(
        "[bold]OpenJarvis[/bold] — type [dim]/exit[/dim] to stop, "
        "[dim]/help[/dim] for commands\n"
    )

    while True:
        try:
            user_input = session.prompt("oj> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if user_input.lower() in ("/exit", "/quit", "exit", "quit"):
            break

        if user_input == "/clear":
            console.clear()
            continue

        if user_input == "/help":
            console.print(
                "  [bold]Commands:[/bold]\n"
                "  [cyan]/exit[/cyan], [cyan]/quit[/cyan]  — exit OpenJarvis\n"
                "  [cyan]/clear[/cyan]           — clear the screen\n"
                "  [cyan]/help[/cyan]            — show this message\n"
                "  [dim]Up/Down[/dim]            — browse input history\n"
                "  [dim]Ctrl-R[/dim]             — reverse history search\n"
            )
            continue

        if not user_input:
            continue

        for event in conductor.chat(user_input):
            render_event(console, event)
