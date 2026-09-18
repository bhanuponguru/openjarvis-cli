# Installation Guide

OpenJarvis can be run instantly via `uvx`, installed as a CLI tool with `uv tool`, installed with standard `pip`, or used via pre-built standalone binaries.

---

## Option 1: Instant Execution with `uvx` (Fastest)

Run OpenJarvis immediately without installing anything permanently:

```bash
uvx openjarvis-cli
```

---

## Option 2: Install via `uv tool` (Recommended)

Install OpenJarvis as an isolated, globally accessible CLI tool:

```bash
uv tool install openjarvis-cli
```

Once installed, simply run:
```bash
openjarvis
# or use the short alias:
oj
```

To update to the latest release:
```bash
uv tool upgrade openjarvis-cli
```

---

## Option 3: Install via `pip`

Install into any Python 3.13+ virtual environment:

```bash
pip install openjarvis-cli
```

---

## Option 4: Standalone Binary (Zero Python Required)

Pre-built binaries include all dependencies and embedded documentation. No Python runtime or build tools are required.

### Download

Download the release archive for your operating system and architecture from [GitHub Releases](https://github.com/bhanuponguru/openjarvis-cli/releases):
- **Linux (x86_64, aarch64)**: `openjarvis-<version>-linux-x86_64.tar.gz`
- **macOS (Apple Silicon arm64, Intel x86_64)**: `openjarvis-<version>-macos-arm64.tar.gz`
- **Windows (x86_64)**: `openjarvis-<version>-windows-x86_64.zip`

### Linux & macOS

```bash
# 1. Extract the release tarball
tar xzf openjarvis-*.tar.gz
cd openjarvis-*

# 2. Make executable if needed
chmod +x openjarvis

# 3. Launch OpenJarvis
./openjarvis

# (Optional) Install system-wide
sudo mv openjarvis /usr/local/bin/
```

### Windows

1. Extract the ZIP archive.
2. Open PowerShell or Command Prompt in the extracted directory.
3. Run `.\openjarvis.exe`.

---

## Option 5: Running from Source with `uv`

If you are developing or prefer running from source:

```bash
# Clone the repository
git clone https://github.com/bhanuponguru/openjarvis-cli.git
cd openjarvis-cli

# Install dependencies and launch
uv sync
uv run openjarvis
```

---

## Next Steps

- **[Quick Start Guide →](quick-start.md)** — Run the setup wizard and start chatting
- **[Configuration Overview →](../configuration/overview.md)** — Configure AI providers
- **[Built-in Tools →](../tools/overview.md)** — Explore all 49 built-in tools

