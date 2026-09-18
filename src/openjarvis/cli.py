"""Interactive CLI for the OpenJarvis Conductor."""

import argparse
import json
import sys
from typing import Any

from prompt_toolkit import prompt
from rich.console import Console

from openjarvis._version import __version__
from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.config_loader import load_config
from openjarvis.setup_wizard import run_wizard
from openjarvis.tool_retriever import ToolRetriever
from openjarvis.tui import render_event, run_repl
from openjarvis.workspace import discover_workspace


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments.
    """
    cli_args = sys.argv[1:] if args is None else args
    console = Console()

    parser = argparse.ArgumentParser(
        prog="openjarvis",
        description="Autonomous multi-model agentic CLI & orchestrator routing tasks across specialized LLMs",
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to specialists.yaml configuration file",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override generalist model name",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Override default provider (e.g. ollama, openai, anthropic)",
    )
    parser.add_argument(
        "--update-tools",
        action="store_true",
        help="Re-index and update tool embedding vectors",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"openjarvis-cli {__version__}",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Optional non-interactive query to execute",
    )

    parsed_args = parser.parse_args(cli_args)

    workspace = discover_workspace()
    workspace.ensure_dirs()

    # Handle --update-tools flag
    if parsed_args.update_tools:
        tools = create_builtin_registry()
        retriever = ToolRetriever(
            registry=tools,
            cache_dir=workspace.global_path("vectors"),
        )
        console.print("[cyan]Updating tool embedding vectors...[/cyan]")
        retriever.build_index()
        console.print(f"[green]✓[/green] Tool vectors saved to [bold]{workspace.global_path('vectors')}[/bold]")
        sys.exit(0)

    try:
        config = load_config(path=parsed_args.config, workspace=workspace)
    except FileNotFoundError:
        # No config found — launch the interactive setup wizard.
        try:
            config_path = run_wizard()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Setup cancelled.[/dim]")
            sys.exit(0)
        try:
            config = load_config(str(config_path), workspace=workspace)
        except (FileNotFoundError, ValueError) as exc:
            Console(stderr=True).print(f"[red]Error loading config:[/red] {exc}")
            sys.exit(1)
    except ValueError as exc:
        Console(stderr=True).print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    # Apply command-line overrides
    if parsed_args.model:
        config.generalist.model = parsed_args.model
    if parsed_args.provider:
        config.generalist.provider = parsed_args.provider

    tools = create_builtin_registry()

    conductor_ref: list[Conductor] = []

    def confirm_tool_permission(tool_name: str, arguments: dict[str, Any], reason: str) -> bool:
        console.print(f"\n[yellow]⚠ Tool Permission Required:[/yellow] [bold]{tool_name}[/bold]")
        console.print(f"  [dim]Reason:[/dim] {reason}")
        if arguments:
            console.print(f"  [dim]Arguments:[/dim] {json.dumps(arguments)}")
        try:
            ans = prompt("Authorize tool execution? ([y]es / [n]o / [a]lways allow / [b]lock): ").strip().lower()
            if ans in ("y", "yes"):
                return True
            elif ans in ("a", "always"):
                if conductor_ref:
                    conductor_ref[0].permissions.remember_decision(tool_name, "allow")
                return True
            elif ans in ("b", "block"):
                if conductor_ref:
                    conductor_ref[0].permissions.remember_decision(tool_name, "deny")
                return False
            return False
        except (EOFError, KeyboardInterrupt):
            return False

    conductor = Conductor(
        config=config,
        tools=tools,
        workspace=workspace,
        confirm_callback=confirm_tool_permission,
    )
    conductor_ref.append(conductor)

    if parsed_args.query:
        query_text = " ".join(parsed_args.query).strip()
        for event in conductor.chat(query_text):
            render_event(console, event)
        return

    run_repl(conductor, console)

