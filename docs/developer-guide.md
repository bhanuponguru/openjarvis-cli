# Developer & Contributing Guide

Technical guide for development environment setup, test suites, static typing, packaging, and standalone binary compilation.

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

## 4. Building Standalone Binaries (PyInstaller)

OpenJarvis CLI can be compiled into a self-contained executable that runs on machines without Python installed:

```bash
# On Linux / macOS:
bash scripts/build-binary.sh

# On Windows:
scripts\build-binary.bat
```

The compiled standalone binary will be placed in `dist/openjarvis`.

---

## 5. Version Management & Releases

OpenJarvis CLI implements **Git-tag and commit-based dynamic versioning** powered by `hatch-vcs`. The version is calculated automatically from Git metadata without needing manually edited version strings:

- **Official Releases**: Pushing an annotated Git tag (e.g. `v{{ version }}`) sets the exact version to `{{ version }}`.
- **Development Builds**: Commits ahead of the latest tag automatically generate PEP 440 dev versions (e.g. `{{ version }}.dev1`) representing the exact commit distance.
- **Build Hook**: `hatch-vcs` automatically generates `src/openjarvis/_version.py` during `uv build` and `uv sync`, embedding the exact calculated version into packages.

### Automated Release Tagging

Use the bumper script to calculate the next SemVer tag, create the annotated Git tag, and build distribution wheels:

```bash
# Calculate next patch release tag (e.g. from v{{ version }}), tag, and build
python scripts/bump-version.py patch

# Calculate next minor release tag (e.g. from v{{ version }}), tag, and build
python scripts/bump-version.py minor

# Calculate next major release tag (e.g. from v{{ version }}), tag, and build
python scripts/bump-version.py major

# Or set an explicit release tag:
python scripts/bump-version.py {{ version }}
```

### Packaging & Distribution Builds

```bash
# 1. Clean build of sdist and wheel
uv build

# 2. Push git tag to GitHub
git push origin v{{ version }}
```

---

## 6. Pre-Commit Verification (Mandatory)

Before committing code or opening a PR, ensure all three mandatory checks pass with zero errors:

```bash
uv run ruff check .
uv run mypy
uv run pytest -q
```

