from pathlib import Path

from openjarvis.workspace import Workspace, discover_workspace


def test_workspace_paths(tmp_path: Path):
    global_dir = tmp_path / ".openjarvis_global"
    local_dir = tmp_path / "project" / ".openjarvis"
    local_dir.mkdir(parents=True)

    ws = Workspace(global_root=global_dir, local_root=local_dir)
    assert ws.global_path("config", "specialists.yaml") == global_dir / "config" / "specialists.yaml"
    assert ws.local_path("config", "specialists.yaml") == local_dir / "config" / "specialists.yaml"


def test_workspace_ensure_dirs(tmp_path: Path):
    global_dir = tmp_path / ".openjarvis_global"
    local_dir = tmp_path / ".openjarvis_local"

    ws = Workspace(global_root=global_dir, local_root=local_dir)
    ws.ensure_dirs()

    assert (global_dir / "config").is_dir()
    assert (global_dir / "memory").is_dir()
    assert (global_dir / "vectors").is_dir()
    assert (global_dir / "models").is_dir()
    assert (local_dir / "config").is_dir()
    assert (local_dir / "memory").is_dir()


def test_workspace_instructions_and_context(tmp_path: Path):
    global_dir = tmp_path / "global"
    global_dir.mkdir()
    local_dir = tmp_path / "local"
    local_dir.mkdir()

    (global_dir / "instructions.md").write_text("Global instruction 1", encoding="utf-8")
    (local_dir / "instructions.md").write_text("Local instruction 2", encoding="utf-8")
    (global_dir / "context.md").write_text("Global context A", encoding="utf-8")
    (local_dir / "context.md").write_text("Local context B", encoding="utf-8")

    ws = Workspace(global_root=global_dir, local_root=local_dir)
    instructions = ws.instructions()
    assert "Global instruction 1" in instructions
    assert "Local instruction 2" in instructions

    context = ws.context()
    assert "Global context A" in context
    assert "Local context B" in context


def test_workspace_config_path_precedence(tmp_path: Path):
    global_dir = tmp_path / "global"
    local_dir = tmp_path / "local"
    (global_dir / "config").mkdir(parents=True)
    (local_dir / "config").mkdir(parents=True)

    g_file = global_dir / "config" / "specialists.yaml"
    l_file = local_dir / "config" / "specialists.yaml"
    g_file.write_text("generalist: ...", encoding="utf-8")
    l_file.write_text("local: ...", encoding="utf-8")

    ws = Workspace(global_root=global_dir, local_root=local_dir)
    assert ws.config_path("specialists.yaml") == l_file

    ws_no_local = Workspace(global_root=global_dir, local_root=None)
    assert ws_no_local.config_path("specialists.yaml") == g_file


def test_discover_workspace(tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    proj = tmp_path / "my_project"
    local_oj = proj / ".openjarvis"
    local_oj.mkdir(parents=True)

    ws = discover_workspace(cwd=proj, home=home)
    assert ws.global_root == home / ".openjarvis"
    assert ws.local_root == local_oj
