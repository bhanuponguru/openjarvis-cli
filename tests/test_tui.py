"""Tests for the prompt_toolkit TUI module."""

from io import StringIO

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from rich.console import Console

from openjarvis import tui


def test_create_session_returns_prompt_session(tmp_path, monkeypatch):
    """create_session() returns a PromptSession with FileHistory."""
    history_path = tmp_path / "history.txt"
    monkeypatch.setattr(tui, "_HISTORY_PATH", history_path)

    session = tui.create_session()

    assert isinstance(session, PromptSession)
    assert isinstance(session.history, FileHistory)


def test_render_event_route(capsys):
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "route", "from_role": "generalist", "to_role": "math"})
    output = console.file.getvalue()
    assert "routing" in output
    assert "generalist" in output
    assert "math" in output


def test_render_event_intermediate_with_content(capsys):
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "intermediate", "content": "thinking...", "role": "math"})
    output = console.file.getvalue()
    assert "thinking..." in output
    assert "math" in output


def test_render_event_intermediate_empty_skipped():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "intermediate", "content": "", "role": "math"})
    output = console.file.getvalue()
    assert output == ""


def test_render_event_tool_call():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "tool_call", "name": "web_search"})
    output = console.file.getvalue()
    assert "web_search" in output


def test_render_event_tool_result_truncation():
    console = Console(file=StringIO(), highlight=False)
    long_result = "x" * 200
    tui.render_event(console, {"type": "tool_result", "result": long_result})
    output = console.file.getvalue()
    assert "…" in output
    assert len(output) < 200


def test_render_event_tool_result_short_no_ellipsis():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "tool_result", "result": "short result"})
    output = console.file.getvalue()
    assert "short result" in output
    assert "…" not in output


def test_render_event_final():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "final", "content": "The answer is 42."})
    output = console.file.getvalue()
    assert "42" in output


def test_render_event_final_empty_skipped():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "final", "content": ""})
    output = console.file.getvalue()
    assert output == ""


def test_render_event_error():
    console = Console(file=StringIO(), highlight=False)
    tui.render_event(console, {"type": "error", "content": "something broke"})
    output = console.file.getvalue()
    assert "something broke" in output


def test_run_repl_exits_on_exit_command(monkeypatch, tmp_path):
    """run_repl exits cleanly when user types /exit."""

    history_path = tmp_path / "history.txt"
    monkeypatch.setattr(tui, "_HISTORY_PATH", history_path)

    inputs = iter(["/exit"])

    def mock_prompt(*args, **kwargs):
        return next(inputs)

    session = tui.create_session()
    monkeypatch.setattr(session, "prompt", mock_prompt)
    monkeypatch.setattr(tui, "create_session", lambda: session)

    class DummyConductor:
        def chat(self, msg):
            yield {"type": "final", "content": "response", "role": "generalist"}

    console = Console(file=StringIO())
    tui.run_repl(DummyConductor(), console)  # type: ignore[arg-type]
    # If we reach here without error, the test passes.


def test_run_repl_exits_on_eof(monkeypatch, tmp_path):
    """run_repl exits cleanly on EOFError (Ctrl-D)."""
    history_path = tmp_path / "history.txt"
    monkeypatch.setattr(tui, "_HISTORY_PATH", history_path)

    def mock_prompt(*args, **kwargs):
        raise EOFError

    session = tui.create_session()
    monkeypatch.setattr(session, "prompt", mock_prompt)
    monkeypatch.setattr(tui, "create_session", lambda: session)

    class DummyConductor:
        def chat(self, msg):
            yield {"type": "final", "content": "response", "role": "generalist"}

    console = Console(file=StringIO())
    tui.run_repl(DummyConductor(), console)  # type: ignore[arg-type]


def test_run_repl_clear_command(monkeypatch, tmp_path):
    """run_repl handles /clear without crashing."""
    history_path = tmp_path / "history.txt"
    monkeypatch.setattr(tui, "_HISTORY_PATH", history_path)

    inputs = iter(["/clear", "/exit"])

    def mock_prompt(*args, **kwargs):
        return next(inputs)

    session = tui.create_session()
    monkeypatch.setattr(session, "prompt", mock_prompt)
    monkeypatch.setattr(tui, "create_session", lambda: session)

    class DummyConductor:
        def chat(self, msg):
            yield {"type": "final", "content": "response", "role": "generalist"}

    console = Console(file=StringIO())
    tui.run_repl(DummyConductor(), console)  # type: ignore[arg-type]
