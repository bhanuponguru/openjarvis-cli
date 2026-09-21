"""Interactive setup wizard for first-run config.yaml creation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError, Validator
from rich.console import Console

from openjarvis.workspace import discover_workspace

_USER_CONFIG = Path.home() / ".openjarvis" / "config.yaml"

_PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "model": "llama3",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "model": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model": "gemini-1.5-pro",
        "api_key_env": "GOOGLE_API_KEY",
    },
    "custom": {
        "base_url": "http://localhost:8000/v1",
        "model": "my-model",
    },
}

_ROOT_AGENT_PROMPT = (
    "You are the Root Agent of OpenJarvis, directly responsible for user communication "
    "and multi-agent orchestration. Spawn specialized child agents with `spawn_agent` "
    "when needed, connect agents with `connect_agents`, monitor their findings, and call `complete_task` "
    "when all children have exited and their work is synthesized."
)

_DEFAULT_AGENTS: dict[str, dict[str, object]] = {
    "researcher": {
        "role": "researcher",
        "description": "Deep factual research, web queries, and knowledge synthesis.",
        "system_prompt": (
            "You are the RESEARCHER agent in OpenJarvis. Gather facts, search documentation, "
            "report findings with `report_findings`, and exit with `exit_agent`."
        ),
        "tools": ["fetch_webpage", "search_web", "query_wikipedia"],
    },
    "coder": {
        "role": "coder",
        "description": "Software engineering, file editing, debugging, and code execution.",
        "system_prompt": (
            "You are the CODER agent in OpenJarvis. Write, debug, refactor, and test code. "
            "Report findings with `report_findings`, and exit with `exit_agent`."
        ),
        "tools": [
            "str_replace_editor",
            "bash",
            "execute_python",
            "lint_python_code",
            "git_status",
            "git_diff",
        ],
    },
    "math": {
        "role": "math",
        "description": "Calculations, numerical derivations, equations, and statistics.",
        "system_prompt": (
            "You are the MATH agent in OpenJarvis. Solve mathematical and numerical tasks. "
            "Report findings with `report_findings`, and exit with `exit_agent`."
        ),
        "tools": [
            "calculator",
            "evaluate_expression",
            "solve_linear_equation",
            "solve_quadratic_equation",
            "convert_units",
            "compute_statistics",
        ],
    },
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

    Creates a complete config.yaml based on user answers.

    Returns:
        Path to the written config file.
    """
    console = Console()
    console.print()
    console.rule("[bold]OpenJarvis Multi-Agent Setup[/bold]")
    console.print(
        "\nWelcome! No [cyan]config.yaml[/cyan] configuration was found.\n"
        "Let's create one so you can start using the OpenJarvis Multi-Agent System.\n"
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
    root_agent: dict[str, object] = {
        "name": "root",
        "role": "coordinator",
        "system_prompt": _ROOT_AGENT_PROMPT,
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "temperature": 0.1,
    }
    if api_key_env:
        root_agent["api_key_env"] = api_key_env

    generalist: dict[str, object] = {
        "name": "generalist",
        "system_prompt": _ROOT_AGENT_PROMPT,
        "provider": provider,
        "base_url": base_url,
        "model": model,
        "delegates_to": list(_DEFAULT_AGENTS.keys()),
    }
    if api_key_env:
        generalist["api_key_env"] = api_key_env

    agents: dict[str, object] = {}
    for name, spec in _DEFAULT_AGENTS.items():
        entry: dict[str, object] = {
            "name": name,
            "role": spec["role"],
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "temperature": 0.0 if name in ("coder", "math") else 0.2,
            "tools": spec["tools"],
        }
        if api_key_env:
            entry["api_key_env"] = api_key_env
        agents[name] = entry

    default_specialists: dict[str, dict[str, Any]] = {
        "math": {
            "description": "Calculations, arithmetic, algebra, calculus, equations, statistics.",
            "system_prompt": "You are the MATH specialist. Solve mathematics and quantitative problems with rigor.",
            "delegates_to": ["code"],
        },
        "code": {
            "description": "Software engineering, writing, analyzing, debugging code.",
            "system_prompt": "You are the CODE specialist. Write, debug, and refactor code.",
            "delegates_to": ["math"],
        },
        "knowledge": {
            "description": "Factual concepts, scientific explanations, definitions, and domain research.",
            "system_prompt": "You are the KNOWLEDGE specialist. Deliver objective and concise factual information.",
            "delegates_to": [],
        },
    }

    specialists: dict[str, Any] = {}
    for name, spec in default_specialists.items():
        delegates = spec.get("delegates_to", [])
        delegates_list = list(delegates) if isinstance(delegates, (list, tuple)) else []
        spec_entry: dict[str, Any] = {
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
            "provider": provider,
            "base_url": base_url,
            "model": model,
            "delegates_to": delegates_list,
        }
        if api_key_env:
            spec_entry["api_key_env"] = api_key_env
        specialists[name] = spec_entry

    config_data = {
        "root_agent": root_agent,
        "generalist": generalist,
        "agents": agents,
        "specialists": specialists,
        "limits": {
            "max_active_agents": 8,
            "max_spawn_depth": 3,
            "max_agent_turns": 15,
            "turn_timeout_seconds": 300.0,
        },
    }

    discover_workspace().ensure_dirs()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.dump(config_data, default_flow_style=False, sort_keys=False))

    console.print()
    console.print(f"[green]✓[/green] Config written to [bold]{output_path}[/bold]")
    console.print("  You can edit it at any time to add or modify agents.\n")

    return output_path
