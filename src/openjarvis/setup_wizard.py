"""Interactive setup wizard for first-run specialists.yaml creation."""

from __future__ import annotations

from pathlib import Path

import yaml
from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError, Validator
from rich.console import Console

from openjarvis.workspace import discover_workspace

_USER_CONFIG = Path.home() / ".openjarvis" / "config" / "specialists.yaml"

_PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "llama3",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "model": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com",
        "model": "gemini-1.5-pro",
        "api_key_env": "GOOGLE_API_KEY",
    },
    "custom": {
        "base_url": "http://localhost:8000/v1",
        "model": "my-model",
    },
}

_GENERALIST_PROMPT = (
    "You are the ROUTER and DISPATCHER of OpenJarvis.\n"
    "Your SOLE responsibility is to analyze the user request and route to the best specialist.\n"
    "CRITICAL: You are NOT a general-purpose solver. Do NOT solve specialized tasks yourself.\n"
    "Route strictly using exactly ONE tag on its own line at the end:\n"
    "- [ROUTE: math] for calculations, arithmetic, algebra, equations, and statistics\n"
    "- [ROUTE: code] for programming, debugging, algorithms, and software engineering\n"
    "- [ROUTE: knowledge] for factual questions, research, and concept explanations\n"
    "- [ROUTE: return] ONLY for basic conversational greetings or delivering the final synthesis."
)

_SPECIALISTS: dict[str, str] = {
    "math": (
        "You are EXCLUSIVELY the MATH specialist of OpenJarvis.\n"
        "Your SOLE job is to solve mathematics, calculations, numerical equations, formal proofs, and statistics.\n"
        "STRICT BOUNDARIES: Act ONLY on mathematical and quantitative tasks. "
        "Do NOT write software application code, do NOT answer general trivia or history, and do NOT engage in casual conversation. "
        "Focus strictly on mathematical derivation. You MUST end your response with [RETURN]."
    ),
    "code": (
        "You are EXCLUSIVELY the CODE specialist of OpenJarvis.\n"
        "Your SOLE job is software engineering: writing, analyzing, debugging, and explaining code, architecture, and algorithms.\n"
        "STRICT BOUNDARIES: Act ONLY on programming tasks. Do NOT perform non-programming domain tasks, essays, or trivia. "
        "For complex manual math derivations, delegate to math using [DELEGATE: math]. "
        "Focus strictly on programming. End your response with [RETURN] or [DELEGATE: math]."
    ),
    "knowledge": (
        "You are EXCLUSIVELY the KNOWLEDGE specialist of OpenJarvis.\n"
        "Your SOLE job is answering factual questions, explaining concepts, and providing domain research.\n"
        "STRICT BOUNDARIES: Act ONLY on factual and informational queries. "
        "Do NOT write functional software or scripts, do NOT solve mathematical equations, and do NOT engage in casual conversation. "
        "Focus strictly on factual explanations. You MUST end your response with [RETURN]."
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
    console.print("  [cyan]ollama[/cyan]     — Local models via Ollama (free, private)")
    console.print("  [cyan]openai[/cyan]     — OpenAI API (GPT-4o, etc.)")
    console.print("  [cyan]anthropic[/cyan]  — Anthropic API (Claude 3.5 Sonnet, etc.)")
    console.print("  [cyan]google[/cyan]     — Google Gemini API (Gemini 1.5 Pro, etc.)")
    console.print("  [cyan]custom[/cyan]     — Any OpenAI-compatible endpoint\n")

    provider = _choose(
        "Provider",
        ["ollama", "openai", "anthropic", "google", "custom"],
        default="ollama",
    )
    preset = _PROVIDER_PRESETS[provider]

    console.print()
    console.print("[bold]Step 2/3 — Configure endpoint and model[/bold]")
    base_url = _ask("API base URL", default=preset.get("base_url", ""))
    model = _ask("Model name", default=preset.get("model", ""))

    default_env = preset.get("api_key_env", "")
    api_key_env: str | None = None
    if provider in ("openai", "anthropic", "google", "custom"):
        raw = _ask("Environment variable holding API key (leave blank to skip)", default=default_env)
        api_key_env = raw if raw else None

    console.print()
    console.print("[bold]Step 3/3 — Where to save the config[/bold]")
    console.print(f"  Default: [dim]{_USER_CONFIG}[/dim]")
    raw_path = _ask("Save location", default=str(_USER_CONFIG))
    output_path = Path(raw_path).expanduser()

    # --- Generate config ---
    generalist: dict = {
        "system_prompt": _GENERALIST_PROMPT,
        "provider": provider,
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
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "delegates_to": ["math"] if name == "code" else [],
        }
        if api_key_env:
            entry["api_key_env"] = api_key_env
        specialists[name] = entry

    config_data = {
        "generalist": generalist,
        "specialists": specialists,
    }

    discover_workspace().ensure_dirs()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(config_data, default_flow_style=False, sort_keys=False))

    console.print()
    console.print(f"[green]✓[/green] Config written to [bold]{output_path}[/bold]")
    console.print("  You can edit it at any time to add or modify specialists.\n")

    return output_path
