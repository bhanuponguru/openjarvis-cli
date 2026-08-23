# Installation Guide

OpenJarvis can be installed via pre-built standalone binaries or via Python's `uv` workspace package manager.

---

## Option 1: Standalone Binary (Recommended)

Pre-built binaries include all dependencies and the embedded user documentation. No Python runtime or build tools are required.

### Download

Download the release archive for your operating system and architecture from GitHub Releases:
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

## Option 2: Running from Source with `uv`

If you are developing or prefer running from source:

```bash
# Clone the repository
git clone https://github.com/bhanuponguru/OpenJarvis.git
cd OpenJarvis

# Install dependencies and launch
uv sync --all-packages
uv run openjarvis
```

---

## What Is Included in Release Packages

- **`openjarvis`**: Self-contained executable CLI binary.
- **`specialists.example.yaml`**: Pre-configured example configuration file.
- **`README.md`**: Quick reference manual.
- **`docs/`**: Complete offline HTML user documentation site.

---

## Next Steps

- **[Quick Start Guide →](quick-start.md)** — Run the setup wizard and start chatting
- **[Configuration Overview →](../configuration/overview.md)** — Configure AI providers
- **[Built-in Tools →](../tools/overview.md)** — Explore all 29 built-in tools
