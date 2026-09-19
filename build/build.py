"""Build script: PyInstaller bundle → standalone openjarvis binary."""

import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_config as config

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "src"
ENTRY_POINT = SOURCE_DIR / "openjarvis" / "__main__.py"


def bundle_pyinstaller(output_dir: Path, target_arch: str | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(ENTRY_POINT),
        "--onefile",
        "--name=openjarvis",
        "--noupx",
        "--noconfirm",
        "--clean",
        f"--distpath={output_dir}",
        f"--workpath={PROJECT_ROOT / 'build' / '_pyinstaller_work'}",
        f"--paths={SOURCE_DIR}",
        "--collect-all=openjarvis",
        "--exclude-module=pytest",
        "--exclude-module=tkinter",
        "--exclude-module=torch",
        "--exclude-module=triton",
        "--exclude-module=nvidia",
        "--exclude-module=cuda",
        *config.get_platform_options(target_arch),
    ]

    print(f"Building binary with PyInstaller on {platform.system()} {platform.machine()}...")
    subprocess.run(cmd, check=True)


def build(output_dir: Path | None = None, target_arch: str | None = None) -> None:
    if output_dir is None:
        output_dir = PROJECT_ROOT / "dist"

    bundle_pyinstaller(output_dir, target_arch=target_arch)

    binary = output_dir / ("openjarvis.exe" if platform.system() == "Windows" else "openjarvis")
    if not binary.exists():
        raise FileNotFoundError(f"Expected binary not found: {binary}")

    print(f"\nBuild complete: {binary}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build OpenJarvis standalone binary")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "dist")
    parser.add_argument(
        "--arch",
        type=str,
        default=None,
        help="Target architecture for macOS (x86_64, arm64, universal2)",
    )
    args = parser.parse_args()

    build(output_dir=args.output_dir, target_arch=args.arch)
