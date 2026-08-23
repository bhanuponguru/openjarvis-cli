from pathlib import Path

from openjarvis.model_types import ToolPermissionConfig
from openjarvis.permissions import PermissionManager
from openjarvis.workspace import Workspace


def test_permission_blocklist_and_allowlist(tmp_path: Path):
    ws = Workspace(global_root=tmp_path / "global", local_root=tmp_path / "local")
    ws.ensure_dirs()

    cfg = ToolPermissionConfig(
        mode="allowlist",
        allowed_tools=["read_file", "search_web"],
        blocked_tools=["run_shell"],
    )
    pm = PermissionManager(config=cfg, workspace=ws)

    # Blocked tool
    dec_block = pm.check("run_shell", {"command": "echo hi"})
    assert dec_block.action == "deny"
    assert dec_block.rule_source == "blocklist"

    # Allowed tool
    dec_allow = pm.check("read_file", {"path": "test.txt"})
    assert dec_allow.action == "allow"
    assert dec_allow.rule_source == "allowlist"

    # Unlisted tool in allowlist mode requires confirmation
    dec_unlisted = pm.check("write_file", {"path": "test.txt", "content": "data"})
    assert dec_unlisted.action == "confirm"


def test_permission_argument_pattern_rules(tmp_path: Path):
    ws = Workspace(global_root=tmp_path / "global", local_root=tmp_path / "local")
    ws.ensure_dirs()

    cfg = ToolPermissionConfig(
        mode="interactive",
        rules={
            "run_shell": {
                "default_action": "deny",
                "argument_patterns": [
                    {"match": {"command": "git *"}, "action": "allow"},
                    {"match": {"command": "*rm *"}, "action": "deny"},
                ],
            }
        },
    )
    pm = PermissionManager(config=cfg, workspace=ws)

    dec_git = pm.check("run_shell", {"command": "git status"})
    assert dec_git.action == "allow"

    dec_rm = pm.check("run_shell", {"command": "rm -rf /tmp/data"})
    assert dec_rm.action == "deny"


def test_remember_decision_persistence(tmp_path: Path):
    ws = Workspace(global_root=tmp_path / "global", local_root=tmp_path / "local")
    ws.ensure_dirs()

    cfg = ToolPermissionConfig(mode="interactive")
    pm = PermissionManager(config=cfg, workspace=ws)

    pm.remember_decision("custom_tool", "allow", scope="global")

    # Reload in fresh manager
    pm2 = PermissionManager(config=ToolPermissionConfig(mode="interactive"), workspace=ws)
    dec = pm2.check("custom_tool", {})
    assert dec.action == "allow"
    assert dec.rule_source == "remembered"
