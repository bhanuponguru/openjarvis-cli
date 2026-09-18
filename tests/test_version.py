"""Tests for versioning and CLI version/help flags."""

import re

import pytest

import openjarvis
from openjarvis import __version__
from openjarvis._version import __version__ as internal_version
from openjarvis.cli import run_cli


def test_version_exports():
    """Verify __version__ is exported and matches _version.py."""
    assert __version__ == internal_version
    assert openjarvis.__version__ == internal_version
    assert re.match(r"^\d+\.\d+\.\d+", __version__)


def test_cli_version_flag(capsys):
    """Verify run_cli(['--version']) outputs version and exits with 0."""
    with pytest.raises(SystemExit) as excinfo:
        run_cli(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert f"openjarvis-cli {__version__}" in captured.out or f"openjarvis-cli {__version__}" in captured.err


def test_cli_help_flag(capsys):
    """Verify run_cli(['--help']) outputs help text and exits with 0."""
    with pytest.raises(SystemExit) as excinfo:
        run_cli(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "usage:" in captured.out.lower() or "usage:" in captured.err.lower()
    assert "--config" in captured.out or "--config" in captured.err
