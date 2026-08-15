# Installation

OpenJarvis can be installed as a pre-built binary (no Python required) or from source.

---

## Option 1: Binary Installation (Recommended)

Pre-built binaries require no Python installation and work out of the box.

### Download

Visit the [GitHub Releases page](https://github.com/bhanuponguru/OpenJarvis/releases) and download the latest version for your platform:

- **Linux:** `openjarvis-X.X.X-linux-x86_64.tar.gz`
- **macOS:** `openjarvis-X.X.X-macos-x86_64.tar.gz`
- **Windows:** `openjarvis-X.X.X-windows-x86_64.zip`

### Linux / macOS

```bash
# Extract the archive
tar xzf openjarvis-*.tar.gz

# Enter the directory
cd openjarvis-*

# Run OpenJarvis
./openjarvis
```

**Optional:** Add to PATH for system-wide access:

```bash
# Move to a directory in your PATH
sudo mv openjarvis /usr/local/bin/

# Now run from anywhere
openjarvis
```

### Windows

1. Extract the ZIP file
2. Double-click `openjarvis.exe` to run
3. Or run from Command Prompt/PowerShell:

```powershell
.\openjarvis.exe
```

**Optional:** Add to PATH:
1. Right-click "This PC" → Properties → Advanced system settings
2. Click "Environment Variables"
3. Edit "Path" and add the directory containing `openjarvis.exe`

---

## Option 2: Install from Source

Installing from source requires Python ≥ 3.13 and the [uv package manager](https://docs.astral.sh/uv/getting-started/installation/).

### Prerequisites

**1. Install Python 3.13+**

- **Linux:** Use your package manager (e.g., `apt install python3.13`)
- **macOS:** `brew install python@3.13`
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

**2. Install uv**

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/bhanuponguru/OpenJarvis.git
cd OpenJarvis

# Install the client package
uv sync --package openjarvis

# Run OpenJarvis
uv run openjarvis
```

### Installing Just the Client

If you only want the OpenJarvis client (no jarvis server):

```bash
cd packages/openjarvis
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install .
openjarvis
```

---

## Verify Installation

After installation, verify OpenJarvis is working:

```bash
openjarvis --version
```

You should see output like:

```
OpenJarvis version 0.1.0
```

---

## What's Included

Binary distributions include:

- **openjarvis** — The main executable
- **specialists.example.yaml** — Sample configuration file
- **README.md** — Quick reference
- **docs/** — Full HTML documentation (this site)
- **LICENSE** — License information

---

## Next Steps

- **[Quick Start →](quick-start.md)** — Get OpenJarvis running in 5 minutes
- **[Configuration →](../configuration/overview.md)** — Set up your AI providers
- **[Built-in Tools →](../tools/overview.md)** — See what OpenJarvis can do

---

## Troubleshooting

### Binary won't run on Linux

**Error:** `Permission denied`

**Solution:** Make the binary executable:

```bash
chmod +x openjarvis
```

### Binary won't run on macOS

**Error:** "openjarvis" cannot be opened because the developer cannot be verified

**Solution:** Allow the app in Security & Privacy:

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine openjarvis

# Or use System Preferences → Security & Privacy → Allow
```

### Binary won't run on Windows

**Error:** Windows Defender blocks the executable

**Solution:** Click "More info" → "Run anyway" in the SmartScreen prompt, or add an exception in Windows Security.

### Source installation fails

**Error:** `uv: command not found`

**Solution:** Install uv first (see prerequisites above), or use pip:

```bash
cd packages/openjarvis
pip install .
```

For more help, see the [Troubleshooting guide](../troubleshooting.md).
