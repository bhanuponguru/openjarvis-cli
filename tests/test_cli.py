"""Tests for the CLI entry point."""

from openjarvis import cli


def test_run_cli_missing_config_launches_wizard(monkeypatch, tmp_path):
    """When no config is found, the setup wizard is launched."""
    from openjarvis.model_types import ConductorConfig, SpecialistConfig
    from openjarvis.tools import ToolRegistry

    dummy_config = ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="You are helpful.")
    )
    config_file = tmp_path / "specialists.yaml"

    monkeypatch.setenv("OJ_CONFIG", "this-file-does-not-exist.yaml")
    monkeypatch.setattr(cli, "run_wizard", lambda: config_file)
    monkeypatch.setattr(cli, "load_config", lambda path=None: dummy_config)
    monkeypatch.setattr(cli, "Conductor", lambda config=None, tools=None: None)
    monkeypatch.setattr(cli, "create_builtin_registry", lambda: ToolRegistry())
    monkeypatch.setattr(cli, "run_repl", lambda conductor, console: None)

    cli.run_cli([])


def test_run_cli_missing_config_wizard_cancelled_exits(monkeypatch):
    """When wizard is cancelled (Ctrl-C), exit with code 0."""
    monkeypatch.setenv("OJ_CONFIG", "this-file-does-not-exist.yaml")
    monkeypatch.setattr(cli, "run_wizard", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))

    try:
        cli.run_cli([])
        raised = False
    except SystemExit as e:
        raised = True
        assert e.code == 0
    assert raised


def test_run_cli_with_existing_config_and_exit(monkeypatch, capsys):
    from openjarvis.model_types import ConductorConfig, SpecialistConfig
    from openjarvis.tools import ToolRegistry

    dummy_config = ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="You are helpful.")
    )

    class DummyConductor:
        def __init__(self, config=None, tools=None):
            self.config = config
            self.tools = tools

        def chat(self, user_input):
            yield {"type": "final", "content": "noop", "role": "generalist"}

    monkeypatch.setattr(cli, "load_config", lambda path=None: dummy_config)
    monkeypatch.setattr(cli, "Conductor", DummyConductor)
    monkeypatch.setattr(cli, "create_builtin_registry", lambda: ToolRegistry())
    monkeypatch.setattr(cli, "run_repl", lambda conductor, console: None)

    cli.run_cli([])

    # Should complete without error (run_repl is a no-op in this test).


def test_run_cli_passes_tools_to_conductor(monkeypatch):
    """Tools from create_builtin_registry must be passed to Conductor."""
    from openjarvis.model_types import ConductorConfig, SpecialistConfig
    from openjarvis.tools import ToolRegistry

    dummy_config = ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="You are helpful.")
    )
    dummy_registry = ToolRegistry()
    captured = {}

    class CapturingConductor:
        def __init__(self, config=None, tools=None):
            captured["tools"] = tools

        def chat(self, user_input):
            yield {"type": "final", "content": "ok", "role": "generalist"}

    monkeypatch.setattr(cli, "load_config", lambda path=None: dummy_config)
    monkeypatch.setattr(cli, "Conductor", CapturingConductor)
    monkeypatch.setattr(cli, "create_builtin_registry", lambda: dummy_registry)
    monkeypatch.setattr(cli, "run_repl", lambda conductor, console: None)

    cli.run_cli([])

    assert captured.get("tools") is dummy_registry
