#!/usr/bin/env python3
"""Automated Git-Tag Semantic Version Bumper for OpenJarvis CLI.

Uses hatch-vcs under the hood. Automatically calculates next version from git tags,
creates annotated git release tags, synchronizes dependencies, and builds wheels.

Usage:
    python scripts/bump-version.py <patch|minor|major|X.Y.Z>

Examples:
    python scripts/bump-version.py patch   # e.g. v0.1.0 -> creates v0.1.1 tag
    python scripts/bump-version.py minor   # e.g. v0.1.0 -> creates v0.2.0 tag
    python scripts/bump-version.py major   # e.g. v0.1.0 -> creates v1.0.0 tag
    python scripts/bump-version.py 0.1.0   # Explicit version tag
"""

from __future__ import annotations

import re
import subprocess
import sys

SEMVER_REGEX = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


def get_latest_tag() -> str:
    """Get the latest git tag, or fallback to '0.0.0' if no tags exist yet."""
    try:
        proc = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip().lstrip("v")
    except Exception:
        return "0.0.0"


def calculate_next_version(current: str, part: str) -> str:
    match = SEMVER_REGEX.match(current)
    if not match:
        raise ValueError(f"Current version '{current}' is not valid SemVer.")

    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        clean = part.lstrip("v")
        if not SEMVER_REGEX.match(clean):
            raise ValueError(f"Invalid bump argument '{part}'. Use patch, minor, major, or X.Y.Z.")
        return clean


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(1 if len(sys.argv) != 2 else 0)

    target = sys.argv[1].strip()
    current = get_latest_tag()
    new_version = calculate_next_version(current, target)
    tag_name = f"v{new_version}"

    print(f"Current latest tag: v{current}")
    print(f"Target release tag: {tag_name}")

    # Check for uncommitted changes
    diff = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if diff.stdout.strip():
        print("\n[WARNING] You have uncommitted changes in git.")
        ans = input("Proceed with tagging anyway? [y/N]: ").strip().lower()
        if ans not in ("y", "yes"):
            print("Aborted.")
            sys.exit(1)

    # Create annotated git tag
    print(f"\nCreating annotated git tag '{tag_name}'...")
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
    print(f"✓ Tag '{tag_name}' created successfully.")

    # Refresh uv and build release distributions
    print("\nSynchronizing environment and building release wheels...")
    subprocess.run(["uv", "sync"], check=True)
    subprocess.run(["uv", "build"], check=True)

    print(f"\n✓ Successfully built openjarvis-cli {new_version}!")
    print("\nPublishing instructions:")
    print(f"  git push origin {tag_name}")
    print("  uv publish")


if __name__ == "__main__":
    main()
