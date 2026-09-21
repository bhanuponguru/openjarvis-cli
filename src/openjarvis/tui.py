"""Terminal UI for the OpenJarvis REPL using prompt_toolkit + Rich."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown

from openjarvis._version import __version__

_COMMANDS = ["/exit", "/quit", "/clear", "/help", "/version", "/update-tools"]
_HISTORY_PATH = Path.home() / ".openjarvis" / "history.txt"
_LEGACY_HISTORY_PATH = Path.home() / ".config" / "openjarvis" / "history.txt"


def create_session() -> PromptSession:
    """Create a prompt_toolkit session with history and command completion."""
    history_path = _HISTORY_PATH
    if not history_path.exists() and _LEGACY_HISTORY_PATH.exists():
        history_path = _LEGACY_HISTORY_PATH
    history_path.parent.mkdir(parents=True, exist_ok=True)
    return PromptSession(
        history=FileHistory(str(history_path)),
        completer=WordCompleter(_COMMANDS, sentence=True),
        enable_history_search=True,
    )


def render_event(console: Console, event: dict[str, Any]) -> None:
    """Render a single Multi-Agent System or Conductor event to the console."""
    etype = event.get("type")

    if etype == "agent_spawned":
        console.print(
            f"  [cyan]🌱 Spawned agent:[/cyan] [bold]{event.get('agent_id')}[/bold] "
            f"([italic]{event.get('role')}[/italic]) — [dim]{event.get('task', '')[:80]}…[/dim]"
        )

    elif etype == "agent_connected":
        console.print(
            f"  [dim]🔗 Connected: {event.get('source_id')} ↔ {event.get('target_id')}[/dim]"
        )

    elif etype == "findings_reported":
        summary = event.get("summary", "")
        sender = event.get("sender_id", "agent")
        console.print(
            f"  [magenta]📢 \\[{sender}] Finding:[/magenta] {summary[:120]}"
        )

    elif etype == "agent_exited":
        aid = event.get("agent_id", "agent")
        console.print(
            f"  [green]✓ \\[{aid}] Exited with artifact:[/green] "
            f"[dim]{event.get('disk_path') or event.get('artifact_id')}[/dim]"
        )

    elif etype == "artifact_saved":
        console.print(
            f"  [green]📦 Artifact saved:[/green] [dim]{event.get('disk_path', '')}[/dim]"
        )

    elif etype == "route":
        from_role = event.get("from_role")
        to_role = event.get("to_role")
        if from_role != "generalist" and to_role != "generalist":
            console.print(
                f"  [cyan]↳ delegating: {from_role} → {to_role}[/cyan]"
            )
        elif to_role == "generalist":
            console.print(
                f"  [dim]↳ returning: {from_role} → {to_role}[/dim]"
            )
        else:
            console.print(
                f"  [dim]↳ routing: {from_role} → {to_role}[/dim]"
            )

    elif etype == "intermediate":
        content = (event.get("content") or "").strip()
        if content:
            role = event.get("role", "agent")
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
        artifacts = event.get("artifacts") or []
        if artifacts:
            console.print("[bold cyan]Generated Artifacts:[/bold cyan]")
            for art in artifacts:
                console.print(f"  • [bold]{art.get('name')}[/bold] ([dim]{art.get('disk_path')}[/dim])")
            console.print()

    elif etype == "error":
        console.print(f"  [red]⚠ {event.get('content', 'unknown error')}[/red]")


def run_repl(system: Any, console: Console, verbose: bool = False) -> None:
    """Run the interactive REPL using prompt_toolkit input and Rich output."""
    session = create_session()
    console.print(
        f"[bold]OpenJarvis Multi-Agent System[/bold] [dim]v{__version__}[/dim] — type [dim]/exit[/dim] to stop, "
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
                "\n[bold]Commands:[/bold]\n"
                "  /help         Show this help message\n"
                "  /clear        Clear the terminal screen\n"
                "  /version      Show OpenJarvis version\n"
                "  /exit, /quit  Exit the CLI\n"
            )
            continue

        if user_input == "/version":
            console.print(f"OpenJarvis v{__version__}")
            continue

        if not user_input:
            continue

        try:
            if verbose:
                for event in system.chat(user_input):
                    render_event(console, event)
            else:
                with console.status("[bold cyan]OpenJarvis agents coordinating...[/bold cyan]"):
                    final_events = list(system.chat(user_input))
                # Render only final or error events
                for event in final_events:
                    if event.get("type") in ("final", "error"):
                        render_event(console, event)
        except Exception as exc:
            console.print(f"[red]Execution error:[/red] {exc}\n")
