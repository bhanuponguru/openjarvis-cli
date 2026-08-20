"""Interactive CLI for the OpenJarvis Conductor."""

import sys

from rich.console import Console

from openjarvis.builtin_tools import create_builtin_registry
from openjarvis.conductor import Conductor
from openjarvis.config_loader import load_config
from openjarvis.setup_wizard import run_wizard
from openjarvis.tui import run_repl


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments (unused, reserved for future
              expansion). The config path is searched in standard locations
              or via OJ_CONFIG environment variable.
    """
    console = Console()

    try:
        config = load_config()
    except FileNotFoundError:
        # No config found — launch the interactive setup wizard.
        try:
            config_path = run_wizard()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Setup cancelled.[/dim]")
            sys.exit(0)
        try:
            config = load_config(str(config_path))
        except (FileNotFoundError, ValueError) as exc:
            Console(stderr=True).print(f"[red]Error loading config:[/red] {exc}")
            sys.exit(1)
    except ValueError as exc:
        Console(stderr=True).print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    tools = create_builtin_registry()
    conductor = Conductor(config=config, tools=tools)

    run_repl(conductor, console)
