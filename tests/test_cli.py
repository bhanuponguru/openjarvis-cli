import builtins

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
    from openjarvis.model_types import ConductorConfig, SpecialistConfig

    dummy_config = ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="You are helpful.")
    )

    # Stub config loading and Conductor so the test doesn't need a real server.
    class DummyConductor:
        def __init__(self, config=None):
            self.config = config

        def chat(self, user_input):
            # Should not be called in this test since input returns 'exit'
            yield {"type": "final", "content": "noop", "role": "generalist"}

    monkeypatch.setattr(cli, "load_config", lambda: dummy_config)
    monkeypatch.setattr(cli, "Conductor", DummyConductor)

    # Simulate user typing 'exit' immediately
    monkeypatch.setattr(builtins, "input", lambda prompt="": "exit")

    cli.run_cli([])

    out = capsys.readouterr().out
    assert "OpenJarvis — type 'exit' or 'quit' to stop" in out
