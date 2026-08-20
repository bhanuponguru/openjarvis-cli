"""Interactive setup wizard for first-run specialists.yaml creation."""

from __future__ import annotations

from pathlib import Path

import yaml
from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError, Validator
from rich.console import Console

_USER_CONFIG = Path.home() / ".config" / "openjarvis" / "specialists.yaml"

_PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
    "custom": {
        "base_url": "http://localhost:8000/v1",
        "model": "my-model",
    },
}

_GENERALIST_PROMPT = (
    "You are a helpful AI assistant that coordinates a team of specialists. "
    "Route requests to the appropriate specialist when needed, or answer directly "
    "when the request is general in nature."
)

_SPECIALISTS: dict[str, str] = {
    "math": (
        "You are a mathematics specialist. Solve equations, explain mathematical "
        "concepts, and work through problems step by step."
    ),
    "code": (
        "You are a software engineering specialist. Write, review, and debug code. "
        "Explain algorithms and software architecture."
    ),
    "knowledge": (
        "You are a knowledge and research specialist. Answer factual questions, "
        "summarize topics, and synthesize information from multiple sources."
    ),
}


class _NonEmptyValidator(Validator):
    def validate(self, document) -> None:
        if not document.text.strip():
            raise ValidationError(message="This field cannot be empty.")


def _ask(prompt_text: str, default: str = "", required: bool = False) -> str:
    """Prompt the user for a value, showing a default."""
    display = f"{prompt_text} [{default}]: " if default else f"{prompt_text}: "
    validator = _NonEmptyValidator() if required else None
    result = prompt(display, validator=validator).strip()
    return result or default


def _choose(prompt_text: str, options: list[str], default: str) -> str:
    """Ask the user to choose from a list of options."""
    opts_str = "/".join(
        f"[{o}]" if o == default else o for o in options
    )
    while True:
        result = prompt(f"{prompt_text} ({opts_str}): ").strip().lower() or default
        if result in options:
            return result
        print(f"  Please choose one of: {', '.join(options)}")  # noqa: T201


def run_wizard() -> Path:
    """Run the interactive first-run setup wizard and return the config path.

    Creates a minimal specialists.yaml based on user answers.

    Returns:
        Path to the written config file.
    """
    console = Console()
    console.print()
    console.rule("[bold]OpenJarvis Setup[/bold]")
    console.print(
        "\nWelcome! No [cyan]specialists.yaml[/cyan] config was found.\n"
        "Let's create one so you can start using OpenJarvis.\n"
    )

    # --- Provider ---
    console.print("[bold]Step 1/3 — Choose your LLM provider[/bold]")
    console.print("  [cyan]ollama[/cyan]  — Local models via Ollama (free, private)")
    console.print("  [cyan]openai[/cyan]  — OpenAI API (requires API key)")
    console.print("  [cyan]custom[/cyan]  — Any OpenAI-compatible endpoint\n")

    provider = _choose("Provider", ["ollama", "openai", "custom"], default="ollama")
    preset = _PROVIDER_PRESETS[provider]

    console.print()
    console.print("[bold]Step 2/3 — Configure endpoint and model[/bold]")
    base_url = _ask("API base URL", default=preset["base_url"])
    model = _ask("Model name", default=preset["model"])

    api_key_env: str | None = None
    if provider in ("openai", "custom"):
        raw = _ask("Environment variable holding API key (leave blank to skip)", default="")
        api_key_env = raw if raw else None

    console.print()
    console.print("[bold]Step 3/3 — Where to save the config[/bold]")
    console.print(f"  Default: [dim]{_USER_CONFIG}[/dim]")
    raw_path = _ask("Save location", default=str(_USER_CONFIG))
    output_path = Path(raw_path).expanduser()

    # --- Generate config ---
    generalist: dict = {
        "system_prompt": _GENERALIST_PROMPT,
        "base_url": base_url,
        "model": model,
        "delegates_to": list(_SPECIALISTS.keys()),
    }
    if api_key_env:
        generalist["api_key_env"] = api_key_env

    specialists: dict = {}
    for name, system_prompt in _SPECIALISTS.items():
        entry: dict[str, object] = {
            "system_prompt": system_prompt,
            "base_url": base_url,
            "model": model,
        }
        if api_key_env:
            entry["api_key_env"] = api_key_env
        specialists[name] = entry

    config_data = {
        "generalist": generalist,
        "specialists": specialists,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(config_data, default_flow_style=False, sort_keys=False))

    console.print()
    console.print(f"[green]✓[/green] Config written to [bold]{output_path}[/bold]")
    console.print("  You can edit it at any time to add or modify specialists.\n")

    return output_path
