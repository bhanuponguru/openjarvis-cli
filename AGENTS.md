# OpenJarvis CLI — Repository Guidelines & Agent Contract

**This is the canonical source of truth for all developers and AI agents working on `openjarvis-cli`.**

## Project Overview

`openjarvis-cli` is an open-source, vendor-agnostic agentic orchestration CLI and terminal client. It routes natural language tasks across a team of specialist LLMs (e.g. generalist, coder, reasoning, terminal execution) orchestrated via a LangGraph state graph.

### Architectural Invariants
1. **Pure Python Architecture**: `openjarvis-cli` is strictly pure Python (target: Python 3.13+ / 3.14). It MUST NEVER import `torch`, `transformers`, or depend on CUDA/GPU hardware.
2. **Provider Agnostic**: Communicates with language models strictly through standard OpenAI-compatible HTTP endpoints or LangChain provider connectors (Ollama, OpenAI, Anthropic, Gemini).
3. **No Demos, No Mocks Policy**: Production tool implementations (e.g. `bash`, `str_replace_editor`, `memory_tools`) must execute real computation and provide real feedback. Mock responses are strictly restricted to isolated unit test fixtures.
4. **Complete Synchronization Invariant**: Every code change modifying behaviors or interfaces must include corresponding documentation updates in `docs/` and test coverage in `tests/` in the same change set.

---

## Build, Test, and Development Commands

- `uv sync --group dev --group docs --group build`: Install package and all tooling groups.
- `uv run openjarvis`: Launch interactive terminal interface with `specialists.yaml`.
- `uv run oj`: Short alias for `openjarvis`.
- `OJ_CONFIG=custom.yaml uv run openjarvis`: Run with a custom specialist configuration.
- `uv run pytest -q`: Run fast test suite (<5s execution time).
- `uv run ruff check .`: Lint and check import formatting.
- `uv run ruff check --fix .`: Auto-fix linting issues.
- `uv run mypy`: Static type-checking across package source.
- `uv run mkdocs serve`: Serve documentation locally on `http://127.0.0.1:8000`.
- `bash scripts/build-binary.sh`: Build compiled standalone executable with Cython + PyInstaller.

---

## Coding Style & Standards

- Target Python 3.13 / 3.14.
- 4-space indentation, type hints on all public interfaces.
- Ruff rules: `E`, `F`, `I`, `UP`, `B`, `SIM` with a 100-character line limit.
- Standard naming: `snake_case` for modules/functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Built-In Tool Preference: Use dedicated built-in editing tools (`replace_file_content`, `write_to_file`, `view_file`) instead of shell hacks.

---

## Pre-Commit Verification (Mandatory)

Before committing or pushing any change, the following verification suite must pass:

```bash
uv run ruff check .
uv run mypy
uv run pytest -q
```

All three must pass cleanly with zero errors.

---

## Modular Agent Guidance (`.agents/`)

- `.agents/rules/architecture.md`: Details on Conductor, LangGraph state engine, Blackboard memory, and the 29 built-in tools.
- `.agents/rules/coding-style.md`: Code style, typing discipline, and tool design rules.
- `.agents/rules/testing-and-verification.md`: Testing guidelines, mock boundaries, and pre-commit checks.

