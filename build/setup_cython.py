"""Cython compilation step: compile all openjarvis .py files to C extensions.

Skips __main__.py so PyInstaller has a pure-Python entry point.
Outputs .so (Linux/macOS) or .pyd (Windows) files alongside the sources.
"""

import shutil
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution
from setuptools.command.build_ext import build_ext

COMPILER_DIRECTIVES = {
    "language_level": "3str",
    "always_allow_keywords": True,
    "annotation_typing": False,
}

# Skip the entry point — PyInstaller needs a pure-Python __main__
SKIP_FILES = {"__main__.py"}


def compile_package(src_dir: Path, output_dir: Path) -> list[Path]:
    """Compile all .py files in src_dir to C extensions in output_dir.

    Returns list of output extension paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    py_files = [
        str(p)
        for p in sorted(src_dir.rglob("*.py"))
        if p.name not in SKIP_FILES
    ]

    if not py_files:
        raise RuntimeError(f"No Python files found under {src_dir}")

    print(f"Cython: compiling {len(py_files)} files from {src_dir}")

    extensions = cythonize(
        py_files,
        compiler_directives=COMPILER_DIRECTIVES,
        nthreads=0,  # auto: use all CPUs
        quiet=False,
        build_dir=str(output_dir / "_cython_build"),
    )

    dist = Distribution({"ext_modules": extensions})
    cmd = build_ext(dist)
    cmd.build_lib = str(output_dir)
    cmd.build_temp = str(output_dir / "_cython_temp")
    cmd.inplace = False
    cmd.ensure_finalized()
    cmd.run()

    # Collect compiled extensions
    ext_suffix = cmd.get_ext_filename("")  # e.g. ".cpython-313-x86_64-linux-gnu.so"
    ext_suffix = ext_suffix.split(".")[-1]  # "so" or "pyd"
    built = list((output_dir).rglob(f"*.{ext_suffix}"))

    print(f"Cython: compiled {len(built)} extensions into {output_dir}")
    return built


def main():
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "packages" / "openjarvis" / "src" / "openjarvis"
    output_dir = project_root / "build" / "cython_out"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    built = compile_package(src_dir, output_dir)
    for ext in built:
        print(f"  {ext.relative_to(project_root)}")


if __name__ == "__main__":
    main()
