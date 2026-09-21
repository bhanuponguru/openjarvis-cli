"""Interactive CLI for the OpenJarvis Multi-Agent System."""

import argparse
import json
import sys
from typing import Any

from prompt_toolkit import prompt
from rich.console import Console

from openjarvis._version import __version__
from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.config_loader import load_config
from openjarvis.multiagent.engine import MultiAgentSystem
from openjarvis.setup_wizard import run_wizard
from openjarvis.tool_retriever import ToolRetriever
from openjarvis.tui import render_event, run_repl
from openjarvis.workspace import discover_workspace

# Conductor alias so tests and external callers can mock/reference it
Conductor: Any = MultiAgentSystem


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments.
    """
    cli_args = sys.argv[1:] if args is None else args
    console = Console()

    parser = argparse.ArgumentParser(
        prog="openjarvis",
        description="Autonomous dynamic Multi-Agent System (MAS) coordinating specialized Conductor agents",
    )
    parser.add_argument(
        "-c", "--config",
        type=str,
        default=None,
        help="Path to config.yaml configuration file",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display live inter-agent messaging, spawning, and tool events",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override root agent model name",
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
        "-y", "--auto-approve",
        action="store_true",
        help="Automatically approve tool executions without prompting",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "autonomous", "allowlist"],
        default=None,
        help="Tool permission enforcement mode (interactive, autonomous, allowlist)",
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
        if config.root_agent:
            config.root_agent.model = parsed_args.model
        config.generalist.model = parsed_args.model
    if parsed_args.provider:
        if config.root_agent:
            config.root_agent.provider = parsed_args.provider
        config.generalist.provider = parsed_args.provider
    if parsed_args.auto_approve:
        config.tool_permissions.mode = "autonomous"
    elif parsed_args.mode:
        config.tool_permissions.mode = parsed_args.mode

    tools = create_builtin_registry()
    system_ref: list[MultiAgentSystem] = []

    def confirm_tool_permission(tool_name: str, arguments: dict[str, Any], reason: str) -> bool:
        if parsed_args.auto_approve or (config.tool_permissions.mode == "autonomous"):
            return True
        console.print(f"\n[yellow]⚠ Tool Permission Required:[/yellow] [bold]{tool_name}[/bold]")
        console.print(f"  [dim]Reason:[/dim] {reason}")
        if arguments:
            console.print(f"  [dim]Arguments:[/dim] {json.dumps(arguments)}")
        try:
            ans = prompt("Authorize tool execution? ([y]es / [n]o / [a]lways allow / [b]lock): ").strip().lower()
            if ans in ("y", "yes"):
                return True
            elif ans in ("a", "always"):
                if system_ref:
                    # Update permission on base config and all live agent conductors
                    system_ref[0].config.tool_permissions.remembered_decisions[tool_name] = "allow"
                    if tool_name not in system_ref[0].config.tool_permissions.allowed_tools:
                        system_ref[0].config.tool_permissions.allowed_tools.append(tool_name)
                    for agent in system_ref[0].agents.values():
                        if hasattr(agent.conductor, "permissions"):
                            agent.conductor.permissions.remember_decision(tool_name, "allow")
                return True
            elif ans in ("b", "block"):
                if system_ref:
                    system_ref[0].config.tool_permissions.remembered_decisions[tool_name] = "deny"
                    for agent in system_ref[0].agents.values():
                        if hasattr(agent.conductor, "permissions"):
                            agent.conductor.permissions.remember_decision(tool_name, "deny")
                return False
            return False
        except (EOFError, KeyboardInterrupt):
            return False

    system = Conductor(
        config=config,
        tools=tools,
        workspace=workspace,
        confirm_callback=confirm_tool_permission,
    )
    system_ref.append(system)

    if parsed_args.query:
        query_text = " ".join(parsed_args.query).strip()
        if parsed_args.verbose:
            for event in system.chat(query_text):
                render_event(console, event)
        else:
            with console.status("[bold cyan]OpenJarvis agents coordinating...[/bold cyan]"):
                events = list(system.chat(query_text))
            for event in events:
                if event.get("type") in ("final", "error"):
                    render_event(console, event)
        return

    if parsed_args.verbose:
        run_repl(system, console, verbose=True)
    else:
        run_repl(system, console)
