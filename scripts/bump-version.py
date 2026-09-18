#!/usr/bin/env python3
"""Automated Semantic Version Bumper for OpenJarvis CLI.

Usage:
    python scripts/bump-version.py <patch|minor|major|X.Y.Z>

Examples:
    python scripts/bump-version.py patch   # 0.2.0 -> 0.2.1
    python scripts/bump-version.py minor   # 0.2.0 -> 0.3.0
    python scripts/bump-version.py major   # 0.2.0 -> 1.0.0
    python scripts/bump-version.py 0.3.0   # Set explicit version
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parent.parent / "src" / "openjarvis" / "_version.py"
SEMVER_REGEX = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


def read_current_version() -> str:
    content = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find __version__ in {VERSION_FILE}")
    return match.group(1)


def write_version(new_version: str) -> None:
    VERSION_FILE.write_text(f'"""Version definition for openjarvis-cli."""\n\n__version__ = "{new_version}"\n', encoding="utf-8")


def bump(current: str, part: str) -> str:
    match = SEMVER_REGEX.match(current)
    if not match:
        raise ValueError(f"Current version '{current}' is not a valid semver.")

    major, minor, patch_num = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch_num + 1}"
    else:
        # Check if explicit version was supplied
        if not SEMVER_REGEX.match(part):
            raise ValueError(f"Invalid bump argument or semver '{part}'. Use patch, minor, major, or X.Y.Z.")
        return part


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1].strip()
    current = read_current_version()
    new_version = bump(current, target)

    write_version(new_version)
    print(f"Bumped openjarvis-cli: {current} → {new_version}")
    print("\nNext steps:")
    print(f"  git commit -am 'chore(release): v{new_version}'")
    print(f"  git tag v{new_version}")
    print("  uv build")
    print("  uv publish")


if __name__ == "__main__":
    main()
