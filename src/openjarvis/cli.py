"""Interactive CLI for the OpenJarvis Conductor."""

import os
import sys

from openjarvis.conductor import Conductor


def run_cli(args: list[str] | None = None) -> None:
    """Run the OpenJarvis interactive CLI.

    Args:
        args: Optional command-line arguments (unused, reserved for future
              expansion). The config path is read from the ``OJ_CONFIG``
              environment variable (default: ``specialists.yaml``).
    """
    config_path = os.environ.get("OJ_CONFIG", "specialists.yaml")

    if not os.path.exists(config_path):
        print(f"Config not found: {config_path}")
        print("Set OJ_CONFIG env var or create specialists.yaml")
        sys.exit(1)

    conductor = Conductor(config_path=config_path)

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
