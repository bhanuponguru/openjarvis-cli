"""Build script: Cython compile + PyInstaller bundle → standalone openjarvis binary.

Pipeline:
  1. Compile packages/openjarvis/**/*.py → .so/.pyd via Cython (per-file, low RAM)
  2. Bundle compiled extensions + Python runtime via PyInstaller (--onefile)
  3. Copy final binary to output_dir/
"""

import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_config as config

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "src"
PKG_DIR = SOURCE_DIR / "openjarvis"
ENTRY_POINT = PKG_DIR / "__main__.py"
CYTHON_OUT_DIR = PROJECT_ROOT / "build" / "cython_out"

_SKIP = {"__main__"}


def _step(msg: str) -> None:
    print(f"\n{'=' * 60}\n{msg}\n{'=' * 60}")


def _hidden_imports() -> list[str]:
    """Derive --hidden-import flags by scanning the source tree.

    PyInstaller cannot trace imports through compiled .so/.pyd extensions, so
    we tell it explicitly which openjarvis modules exist. Scanning the source
    tree means this stays correct as modules are added or removed — no list to
    maintain by hand.
    """
    flags = []
    for py in sorted(PKG_DIR.rglob("*.py")):
        mod = str(py.relative_to(SOURCE_DIR)).replace("/", ".").replace("\\", ".").removesuffix(".py")
        if mod.split(".")[-1] not in _SKIP:
            flags.append(f"--hidden-import={mod}")
    return flags


def _add_binaries() -> list[str]:
    """Derive --add-binary flags for every compiled Cython extension.

    Each extension must land in the bundle at the same relative path it has
    under cython_out/ so the import machinery resolves it as the right module.
    """
    sep = ";" if sys.platform == "win32" else ":"
    flags = []
    for ext in sorted(CYTHON_OUT_DIR.rglob("*.so")):
        dest = str(ext.relative_to(CYTHON_OUT_DIR).parent) or "openjarvis"
        flags.append(f"--add-binary={ext}{sep}{dest}")
    for ext in sorted(CYTHON_OUT_DIR.rglob("*.pyd")):
        dest = str(ext.relative_to(CYTHON_OUT_DIR).parent) or "openjarvis"
        flags.append(f"--add-binary={ext}{sep}{dest}")
    return flags


def compile_cython() -> None:
    _step("Step 1: Cython compile")
    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "setup_cython.py")],
        check=True,
    )


def bundle_pyinstaller(output_dir: Path, target_arch: str | None = None) -> None:
    _step("Step 2: PyInstaller bundle")
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(ENTRY_POINT),
        "--onefile",
        "--name=openjarvis",
        "--noupx",
        "--noconfirm",
        "--clean",
        f"--distpath={output_dir}",
        f"--workpath={PROJECT_ROOT / 'build' / '_pyinstaller_work'}",
        f"--paths={SOURCE_DIR}",
        f"--paths={CYTHON_OUT_DIR}",
        *_hidden_imports(),
        *_add_binaries(),
        "--exclude-module=pytest",
        "--exclude-module=setuptools",
        "--exclude-module=pip",
        "--exclude-module=wheel",
        "--exclude-module=unittest",
        "--exclude-module=tkinter",
        "--exclude-module=nuitka",
        "--exclude-module=jarvis",
        "--exclude-module=torch",
        "--exclude-module=triton",
        "--exclude-module=nvidia",
        "--exclude-module=cuda",
        *config.get_platform_options(target_arch),
    ]

    print(f"Platform: {platform.system()} {platform.machine()}")
    subprocess.run(cmd, check=True)


def build(output_dir: Path | None = None, target_arch: str | None = None) -> None:
    if output_dir is None:
        output_dir = PROJECT_ROOT / "dist"

    compile_cython()
    bundle_pyinstaller(output_dir, target_arch=target_arch)

    binary = output_dir / ("openjarvis.exe" if platform.system() == "Windows" else "openjarvis")
    if not binary.exists():
        raise FileNotFoundError(f"Expected binary not found: {binary}")

    print(f"\nBuild complete: {binary}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build OpenJarvis standalone binary")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "dist")
    parser.add_argument("--arch", type=str, default=None,
                        help="Target architecture for macOS (x86_64, arm64, universal2)")
    args = parser.parse_args()

    build(output_dir=args.output_dir, target_arch=args.arch)
