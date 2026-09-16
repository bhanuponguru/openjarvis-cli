"""Unit tests for OpenJarvis git tools."""

import os
import subprocess
from pathlib import Path

from openjarvis.builtin_tools.git_tools import (
    apply_patch,
    git_diff,
    git_log,
    git_status,
)


def test_git_tools_in_repo(tmp_path: Path):
    # Initialize a temporary git repository
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_path), capture_output=True, check=True)

    test_file = tmp_path / "hello.txt"
    test_file.write_text("version 1\n")
    subprocess.run(["git", "add", "hello.txt"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=str(tmp_path), capture_output=True, check=True)

    # Modify file
    test_file.write_text("version 2\n")

    # Run git tools in cwd=tmp_path
    orig_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        status = git_status()
        assert "hello.txt" in status

        diff = git_diff()
        assert "-version 1" in diff
        assert "+version 2" in diff

        log_out = git_log(max_count=2)
        assert "initial commit" in log_out
    finally:
        os.chdir(orig_cwd)


def test_apply_patch(tmp_path: Path):
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(tmp_path), capture_output=True, check=True)

    f = tmp_path / "file.txt"
    f.write_text("line A\nline B\n")
    subprocess.run(["git", "add", "file.txt"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "commit 1"], cwd=str(tmp_path), capture_output=True, check=True)

    patch_text = """diff --git a/file.txt b/file.txt
--- a/file.txt
+++ b/file.txt
@@ -1,2 +1,2 @@
 line A
-line B
+line C
"""
    orig_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        res = apply_patch(patch_text)
        assert "Successfully applied patch" in res
        assert f.read_text() == "line A\nline C\n"
    finally:
        os.chdir(orig_cwd)


def test_apply_empty_patch():
    assert "Error: Empty patch provided." in apply_patch("")
