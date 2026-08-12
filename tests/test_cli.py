import builtins
import os

from openjarvis import cli


def test_run_cli_missing_config(monkeypatch):
    # Ensure a non-existent config causes sys.exit(1)
    monkeypatch.setenv("OJ_CONFIG", "this-file-does-not-exist.yaml")
    try:
        cli.run_cli([])
        raised = False
    except SystemExit as e:
        raised = True
        assert e.code == 1
    assert raised


def test_run_cli_with_existing_config_and_exit(monkeypatch, tmp_path, capsys):
    # Create a dummy config file so os.path.exists passes
    cfg = tmp_path / "specialists.yaml"
    cfg.write_text("# minimal config placeholder\n")

    # Replace the Conductor with a lightweight dummy to avoid loading real configs
    class DummyConductor:
        def __init__(self, config_path=None):
            self.config_path = config_path

        def chat(self, user_input):
            # Should not be called in this test since input returns 'exit'
            yield {"type": "final", "content": "noop", "role": "generalist"}

    monkeypatch.setenv("OJ_CONFIG", str(cfg))
    monkeypatch.setattr(cli, "Conductor", DummyConductor)

    # Simulate user typing 'exit' immediately
    monkeypatch.setattr(builtins, "input", lambda prompt="": "exit")

    cli.run_cli([])

    out = capsys.readouterr().out
    assert "OpenJarvis — type 'exit' or 'quit' to stop" in out
