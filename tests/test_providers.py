from unittest.mock import MagicMock, patch

import pytest

from openjarvis.providers import call_llm
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
    """Mock httpx and verify response parsing."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello world"}}]
    }

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        result = call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

    assert result == "Hello world"


def test_call_llm_sends_correct_payload(config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "ok"}}]
    }

    with patch("httpx.Client") as mock_client:
        mock_post = mock_client.return_value.__enter__.return_value.post
        mock_post.return_value = mock_response
        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["json"]["model"] == "test-model"
        assert call_kwargs["json"]["messages"] == [
            {"role": "system", "content": "You are test"},
            {"role": "user", "content": "hi"},
        ]
        assert call_kwargs["json"]["temperature"] == 0.5


def test_call_llm_uses_api_key_header(config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}

    with patch("httpx.Client") as mock_client:
        mock_post = mock_client.return_value.__enter__.return_value.post
        mock_post.return_value = mock_response
        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
            api_key="sk-test-key",
        )

        headers = mock_post.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer sk-test-key"


def test_call_llm_raises_on_http_error(config):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = Exception("401 Unauthorized")

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        with pytest.raises(Exception, match="401"):
            call_llm(
                messages=[{"role": "user", "content": "hi"}],
                config=config,
            )


def test_call_llm_constructs_full_messages_with_system_prompt(config):
    """System prompt should be prepended as a system message."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}

    with patch("httpx.Client") as mock_client:
        mock_post = mock_client.return_value.__enter__.return_value.post
        mock_post.return_value = mock_response
        call_llm(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )

        sent_messages = mock_post.call_args.kwargs["json"]["messages"]
        assert sent_messages[0]["role"] == "system"
        assert sent_messages[0]["content"] == "You are test"
        assert sent_messages[1] == {"role": "user", "content": "hi"}
