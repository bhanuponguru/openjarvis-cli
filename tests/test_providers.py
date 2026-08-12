from unittest.mock import MagicMock, patch

import pytest

from openjarvis.providers import call_llm, call_llm_stream
from openjarvis.types import SpecialistConfig


@pytest.fixture
def config():
    return SpecialistConfig(
        name="test",
        system_prompt="You are test",
        base_url="http://test-server/v1",
        model="test-model",
        temperature=0.5,
    )


def test_call_llm_returns_content(config):
    """Mock OpenAI SDK and verify response parsing."""
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "Hello world"

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_completion

        result = call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

    assert result == "Hello world"


def test_call_llm_sends_correct_payload(config):
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "ok"

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_completion

        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "test-model"
        assert call_kwargs["messages"] == [
            {"role": "system", "content": "You are test"},
            {"role": "user", "content": "hi"},
        ]
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["stream"] is False


def test_call_llm_uses_api_key(config):
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "ok"

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_completion

        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
            api_key="sk-test-key",
        )

        # Verify OpenAI client was constructed with the API key
        assert mock_openai_class.call_args.kwargs["api_key"] == "sk-test-key"


def test_call_llm_constructs_full_messages_with_system_prompt(config):
    """System prompt should be prepended as a system message."""
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "ok"

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_completion

        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

        sent_messages = mock_client.chat.completions.create.call_args.kwargs["messages"]
        assert sent_messages[0]["role"] == "system"
        assert sent_messages[0]["content"] == "You are test"
        assert sent_messages[1] == {"role": "user", "content": "hi"}


def test_call_llm_stream_yields_deltas(config):
    """Streaming should yield content deltas from chunks."""
    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock()]
    mock_chunk1.choices[0].delta.content = "Hello"

    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock()]
    mock_chunk2.choices[0].delta.content = " world"

    mock_chunk3 = MagicMock()
    mock_chunk3.choices = [MagicMock()]
    mock_chunk3.choices[0].delta.content = None  # Finish marker

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = iter([mock_chunk1, mock_chunk2, mock_chunk3])

        result = list(call_llm_stream(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        ))

    assert result == ["Hello", " world"]


def test_call_llm_stream_sends_stream_true(config):
    """Streaming calls should set stream=True."""
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "ok"

    with patch("openjarvis.providers.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = iter([mock_chunk])

        list(call_llm_stream(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        ))

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["stream"] is True
