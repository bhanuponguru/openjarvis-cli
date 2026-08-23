from pathlib import Path

import pytest

from openjarvis.builtin_tools.memory_tools import (
    delete_memory,
    delete_note,
    list_memories,
    list_notes,
    read_memory,
    recall_note,
    save_memory,
    search_memories,
    store_note,
    update_memory,
)
from openjarvis.workspace import Workspace, set_current_workspace


@pytest.fixture(autouse=True)
def setup_workspace(tmp_path: Path):
    global_dir = tmp_path / ".openjarvis_global"
    local_dir = tmp_path / "proj" / ".openjarvis"
    ws = Workspace(global_root=global_dir, local_root=local_dir)
    ws.ensure_dirs()
    set_current_workspace(ws)
    yield ws
    set_current_workspace(None)


def test_memory_crud_local():
    # Create
    res = save_memory("project_plan", "# Project Plan\nDeliver by Q3", scope="local")
    assert "Saved memory" in res

    # Read
    content = read_memory("project_plan", scope="local")
    assert "Deliver by Q3" in content

    # Update (append)
    update_res = update_memory("project_plan", "Budget approved.", scope="local")
    assert "Updated memory" in update_res
    updated_content = read_memory("project_plan", scope="local")
    assert "Deliver by Q3" in updated_content
    assert "Budget approved." in updated_content

    # List
    mems = list_memories(scope="local")
    assert "project_plan" in mems

    # Search
    search_res = search_memories("budget", scope="local")
    assert len(search_res) == 1
    assert search_res[0]["name"] == "project_plan"

    # Delete
    del_res = delete_memory("project_plan", scope="local")
    assert "Deleted memory" in del_res
    assert "not found" in read_memory("project_plan", scope="local")


def test_memory_global_scope():
    save_memory("user_profile", "User prefers concise answers", scope="global")
    content = read_memory("user_profile", scope="global")
    assert "User prefers concise answers" in content

    # Read fallback from local to global
    fallback_content = read_memory("user_profile", scope="local")
    assert "User prefers concise answers" in fallback_content


def test_backward_compatible_aliases():
    res = store_note("quick_key", "quick value")
    assert "Saved memory" in res
    assert recall_note("quick_key") == "quick value"
    assert "quick_key" in list_notes()
    delete_note("quick_key")
    assert "not found" in recall_note("quick_key")
