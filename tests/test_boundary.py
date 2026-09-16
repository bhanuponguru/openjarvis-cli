import ast
from pathlib import Path


def _get_imports(filepath: Path) -> set[str]:
    """Parse a python file and return all imported top-level module names."""
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    except Exception as e:
        raise RuntimeError(f"Failed to parse {filepath}: {e}") from e

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])
    return modules


def test_openjarvis_package_boundary():
    """Package Boundary Invariant: openjarvis must never import jarvis, torch, or transformers."""
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    assert src_dir.exists(), f"Source directory {src_dir} does not exist"

    forbidden = {"jarvis", "torch", "transformers"}
    violations: list[str] = []
    for py_file in src_dir.rglob("*.py"):
        imports = _get_imports(py_file)
        leaked = imports.intersection(forbidden)
        if leaked:
            violations.append(f"{py_file.relative_to(repo_root)} imports {leaked}")

    assert not violations, f"openjarvis violated package boundary: {violations}"
