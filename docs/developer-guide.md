# Developer & Contributing Guide

Thank you for contributing to OpenJarvis CLI! This guide covers setting up your development environment, running tests, linting, and building standalone binaries.

---

## 1. Development Setup

OpenJarvis CLI uses Python 3.13+ and [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management:

```bash
# Clone the repository
git clone https://github.com/bhanuponguru/openjarvis-cli.git
cd openjarvis-cli

# Install dependencies and development groups
uv sync --group dev --group docs --group build
```

---

## 2. Running the Test Suite

All tests execute on standard CPUs in seconds without any external model requirements:

```bash
# Run all unit tests
uv run pytest -q

# Run with verbose output
uv run pytest -v
```

---

## 3. Linting & Type Checking

Before submitting a PR, verify linting and type safety:

```bash
# Run Ruff linting
uv run ruff check .

# Auto-fix import sorting and common issues
uv run ruff check --fix .

# Static type checking
uv run mypy
```

---

## 4. Building Standalone Binaries (Cython + PyInstaller)

OpenJarvis CLI can be compiled into a self-contained executable that runs on machines without Python installed:

```bash
# On Linux / macOS:
bash scripts/build-binary.sh

# On Windows:
scripts\build-binary.bat
```

The compiled standalone binary will be placed in `dist/openjarvis`.
