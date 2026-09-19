"""Build configuration for PyInstaller pipeline."""

import platform
import sys


def get_platform_options(target_arch: str | None = None) -> list[str]:
    """Return PyInstaller flags for the current platform.

    Args:
        target_arch: Target architecture override (x86_64, arm64, universal2).
                     Defaults to the current machine architecture on macOS.
    """
    if sys.platform == "darwin":
        arch = target_arch or platform.machine()
        return [f"--target-arch={arch}", "--strip"]
    elif sys.platform == "win32":
        return []
    else:
        return ["--strip"]


# Module-level constant using the detected architecture (backwards compat).
PLATFORM_OPTIONS: list[str] = get_platform_options()
