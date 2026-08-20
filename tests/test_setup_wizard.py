"""Tests for the interactive setup wizard."""

import yaml

from openjarvis import setup_wizard
from openjarvis.config_loader import load_config


def _make_inputs(*values):
    """Return a mock for prompt() that yields values in order."""
    it = iter(values)

    def mock_prompt(prompt_text="", **kwargs):
        return next(it)

    return mock_prompt


def test_wizard_ollama_defaults_generates_valid_config(monkeypatch, tmp_path):
    """Wizard with Ollama defaults writes a config that load_config accepts."""
    output_file = tmp_path / "specialists.yaml"

    # Simulate: provider=ollama, base_url=<default>, model=<default>,
    # save_path=<tmp>, no api key
    inputs = _make_inputs(
        "ollama",                     # provider choice
        "",                           # base_url: accept default
        "",                           # model: accept default
        str(output_file),             # save location
    )
    monkeypatch.setattr(setup_wizard, "prompt", inputs)
    monkeypatch.setattr(setup_wizard, "_USER_CONFIG", tmp_path / "specialists.yaml")

    result_path = setup_wizard.run_wizard()

    assert result_path == output_file
    assert output_file.exists()

    # Must load without error
    config = load_config(str(output_file))
    assert config.generalist is not None
    assert len(config.specialists) >= 1


def test_wizard_openai_writes_api_key_env(monkeypatch, tmp_path):
    """Wizard with OpenAI provider includes api_key_env in the written config."""
    output_file = tmp_path / "specialists.yaml"

    inputs = _make_inputs(
        "openai",                     # provider
        "",                           # base_url: accept default
        "",                           # model: accept default
        "OPENAI_API_KEY",             # api_key_env
        str(output_file),             # save path
    )
    monkeypatch.setattr(setup_wizard, "prompt", inputs)
    monkeypatch.setattr(setup_wizard, "_USER_CONFIG", tmp_path / "specialists.yaml")

    setup_wizard.run_wizard()

    raw = yaml.safe_load(output_file.read_text())
    assert raw["generalist"].get("api_key_env") == "OPENAI_API_KEY"


def test_wizard_custom_provider(monkeypatch, tmp_path):
    """Wizard accepts a custom URL and model name."""
    output_file = tmp_path / "specialists.yaml"

    inputs = _make_inputs(
        "custom",                              # provider
        "http://my-server:8080/v1",            # base_url
        "mistral-7b",                          # model
        "MY_API_KEY",                          # api_key_env
        str(output_file),                      # save path
    )
    monkeypatch.setattr(setup_wizard, "prompt", inputs)
    monkeypatch.setattr(setup_wizard, "_USER_CONFIG", tmp_path / "specialists.yaml")

    setup_wizard.run_wizard()

    raw = yaml.safe_load(output_file.read_text())
    assert raw["generalist"]["base_url"] == "http://my-server:8080/v1"
    assert raw["generalist"]["model"] == "mistral-7b"


def test_wizard_config_roundtrips_through_load_config(monkeypatch, tmp_path):
    """Any config written by the wizard must survive a full load_config() pass."""
    output_file = tmp_path / "specialists.yaml"

    inputs = _make_inputs(
        "ollama", "", "", str(output_file)
    )
    monkeypatch.setattr(setup_wizard, "prompt", inputs)
    monkeypatch.setattr(setup_wizard, "_USER_CONFIG", tmp_path / "specialists.yaml")

    path = setup_wizard.run_wizard()
    config = load_config(str(path))

    # Generalist must be present; all default specialists must be loadable
    assert config.generalist.name == "generalist"
    assert "math" in config.specialists
    assert "code" in config.specialists
    assert "knowledge" in config.specialists
