"""Interactive CLI for the OpenJarvis Conductor."""

import sys

from openjarvis.conductor import Conductor
from openjarvis.config_loader import load_config


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments (unused, reserved for future
              expansion). The config path is searched in standard locations
              or via OJ_CONFIG environment variable.
    """
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    conductor = Conductor(config=config)

    print("OpenJarvis — type 'exit' or 'quit' to stop")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in ("exit", "quit"):
            break

        if not user_input:
            continue

        # Process and show intermediate steps
        for event in conductor.chat(user_input):
            if event["type"] == "route":
                print(f"  ──→ [{event['from_role']}] → [{event['to_role']}]")
            elif event["type"] == "intermediate":
                print(f"  [{event['role']}]: {event['content'][:200]}")
            elif event["type"] == "final":
                print(f"  [{event['role']}]: {event['content']}")
            elif event["type"] == "error":
                print(f"  ⚠ Error: {event['content']}")
