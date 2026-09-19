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

# Install build dependencies
echo "Installing build dependencies..."
uv sync --group build

# Run build
echo "Building binary..."
uv run python build/build.py --output-dir "$OUTPUT_DIR"

echo "Build complete!"
