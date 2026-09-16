"""Unit tests for str_replace_editor tool in openjarvis."""

from pathlib import Path

from openjarvis.builtin_tools.editor_tools import execute_bash, str_replace_editor


def test_editor_create_and_view(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    res = str_replace_editor(
        command="create",
        path=str(test_file),
        file_text="line 1\nline 2\nline 3\nline 4\nline 5\n",
    )
    assert "File created successfully" in res
    assert test_file.exists()

    # View full file
    view_out = str_replace_editor(command="view", path=str(test_file))
    assert "1 | line 1" in view_out
    assert "5 | line 5" in view_out

    # View range [2, 4]
    view_sub = str_replace_editor(command="view", path=str(test_file), view_range=[2, 4])
    assert "1 | line 1" not in view_sub
    assert "2 | line 2" in view_sub
    assert "4 | line 4" in view_sub


def test_editor_str_replace_and_undo(tmp_path: Path):
    test_file = tmp_path / "replace_test.txt"
    str_replace_editor(
        command="create",
        path=str(test_file),
        file_text="alpha beta gamma",
    )

    # Valid replacement
    rep_res = str_replace_editor(
        command="str_replace",
        path=str(test_file),
        old_str="beta",
        new_str="DELTA",
    )
    assert "Successfully replaced" in rep_res
    assert test_file.read_text(encoding="utf-8") == "alpha DELTA gamma"

    # Non-unique replacement failure
    dup_file = tmp_path / "dup.txt"
    str_replace_editor(command="create", path=str(dup_file), file_text="foo bar foo")
    dup_res = str_replace_editor(command="str_replace", path=str(dup_file), old_str="foo", new_str="baz")
    assert "Error" in dup_res and "appears 2 times" in dup_res

    # Undo edit
    undo_res = str_replace_editor(command="undo_edit", path=str(test_file))
    assert "Successfully reverted" in undo_res
    assert test_file.read_text(encoding="utf-8") == "alpha beta gamma"


def test_editor_insert(tmp_path: Path):
    test_file = tmp_path / "insert_test.txt"
    str_replace_editor(
        command="create",
        path=str(test_file),
        file_text="line 1\nline 2\n",
    )

    ins_res = str_replace_editor(
        command="insert",
        path=str(test_file),
        insert_line=1,
        new_str="inserted line",
    )
    assert "Successfully inserted" in ins_res
    lines = test_file.read_text(encoding="utf-8").splitlines()
    assert lines == ["line 1", "inserted line", "line 2"]


def test_execute_bash_basic():
    res = execute_bash("echo 'hello openjarvis'")
    assert "Exit code: 0" in res
    assert "hello openjarvis" in res


def test_execute_bash_nonzero_exit():
    res = execute_bash("exit 42")
    assert "Exit code: 42" in res


def test_execute_bash_timeout():
    res = execute_bash("sleep 2", timeout_seconds=1)
    assert "Error: Command timed out after 1 seconds" in res

