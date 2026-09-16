#!/usr/bin/env bash
# Build OpenJarvis standalone binary for current platform

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Parse arguments
OUTPUT_DIR="dist"

while [[ $# -gt 0 ]]; do
  case $1 in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--output-dir DIR]"
      exit 1
      ;;
  esac
done

# Check platform toolchain
echo "Checking build toolchain..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  if ! command -v gcc &> /dev/null; then
    echo "Error: gcc not found. Install build-essential:"
    echo "  sudo apt-get install build-essential"
    exit 1
  fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
  if ! command -v clang &> /dev/null; then
    echo "Error: clang not found. Install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
  fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  if ! command -v gcc &> /dev/null && ! command -v cl &> /dev/null; then
    echo "Error: No C compiler found. Install MinGW64 or Visual Studio Build Tools"
    exit 1
  fi
fi

# Install build dependencies
echo "Installing build dependencies..."
uv sync --group build

# Run build
echo "Building binary..."
uv run python build/build.py --output-dir "$OUTPUT_DIR"

echo "Build complete!"
