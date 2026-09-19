# Installation Guide

OpenJarvis can be run using pre-built standalone binaries (zero Python required) or run directly from source using `uv`.

---

## Option 1: Standalone Binary (Zero Python Required)

Pre-built binaries include all dependencies and embedded documentation. No Python runtime or build tools are required.

### Download

Download the release archive for your operating system and architecture from [GitHub Releases](https://github.com/bhanuponguru/openjarvis-cli/releases):
- **Linux (x86_64)**: `openjarvis-v{{ version }}-linux-x86_64.tar.gz`
- **macOS (Apple Silicon arm64)**: `openjarvis-v{{ version }}-macos-arm64.tar.gz`
- **Windows (x86_64)**: `openjarvis-v{{ version }}-windows-x86_64.zip`

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

## Option 2: Running from Source with `uv`

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

