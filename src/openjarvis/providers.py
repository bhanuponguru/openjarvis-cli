from collections.abc import Iterator
from typing import Any

from openai import OpenAI

from openjarvis.types import SpecialistConfig


def _get_choice_message(choice: Any) -> Any:
    """Return the message object (or dict) for a choice, or None.

    Handles both object-attribute and dict-like shapes from differing SDKs.
    """
    # attribute-style
    message = getattr(choice, "message", None)
    if message is not None:
        return message
    # dict-like
    try:
        return choice.get("message")
    except Exception:
        return None


def _extract_content_from_completion(completion: Any, tools: list[dict] | None) -> Any:
    """Normalize various SDK completion shapes to either a content string
    or a message-like object when tools are in use.
    """
    # Try the common attribute-heavy SDK shape
    try:
        choice = completion.choices[0]
    except Exception:
        # Fallback for dict-like responses
        if isinstance(completion, dict):
            choices = completion.get("choices") or []
            choice = choices[0] if choices else {}
        else:
            choice = {}

    msg = _get_choice_message(choice)
    # If tools are used the caller expects a message object so return the
    # message as-is (dict or object). Otherwise prefer returning a plain
    # content string when available.
    if tools is not None:
        return msg or choice

    # Prefer attribute access, but fall back to mapping lookups.
    content = None
    if msg is not None:
        content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
    if content is None:
        content = getattr(choice, "text", None) or (choice.get("text") if isinstance(choice, dict) else None)
    return content or ""


def call_llm(
    messages: list[dict],
    config: SpecialistConfig,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stop: list[str] | None = None,
    response_format: dict | None = None,
    tools: list[dict] | None = None,
) -> Any:
    """Call an OpenAI-compatible LLM API and return the response.

    When ``tools`` is not supplied the return value is a plain string.  When
    tools are supplied the return is a ``chat.CompletionMessage`` (from the
    OpenAI SDK), so callers can inspect ``tool_calls`` on it.

    Args:
        messages: Message dicts with "role" and "content". Roles must already be
            valid API roles -- translation from internal speaker names happens in
            the conductor, not here.
        config: SpecialistConfig supplying base_url, model, and the defaults for
            every override below.
        api_key: Optional API key for Bearer authentication.
        temperature, max_tokens, stop, response_format: per-call overrides;
            None means "use the specialist's configured value".
        tools: OpenAI-format tools list. When supplied the return type changes
            from ``str`` to ``ChatCompletionMessage`` so the caller can inspect
            ``tool_calls``.

    Raises:
        openai.APIError: On API errors (connection, auth, rate limit, etc).
    """
    client = OpenAI(
        base_url=config.base_url,
        api_key=api_key or "none",  # SDK requires a value; "none" works for unauthenticated servers
        timeout=config.timeout,
    )

    resolved_temperature = config.temperature if temperature is None else temperature
    resolved_max_tokens = config.max_tokens if max_tokens is None else max_tokens
    resolved_stop = config.stop if stop is None else stop

    # Build kwargs dynamically to avoid None values
    kwargs: dict = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            *messages,
        ],
        "temperature": resolved_temperature,
        "stream": False,
    }

    if resolved_max_tokens is not None:
        kwargs["max_tokens"] = resolved_max_tokens
    if resolved_stop:
        kwargs["stop"] = resolved_stop
    if response_format is not None:
        kwargs["response_format"] = response_format
    if tools is not None:
        kwargs["tools"] = tools

    completion = client.chat.completions.create(**kwargs)
    return _extract_content_from_completion(completion, tools)


def call_llm_stream(
    messages: list[dict],
    config: SpecialistConfig,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stop: list[str] | None = None,
    response_format: dict | None = None,
    tools: list[dict] | None = None,
) -> Iterator[str]:
    """Same as :func:`call_llm`, but yields content deltas as they arrive.

    Note: when tools are provided the model may return a tool_calls message
    instead of content. In that case the stream yields the empty string and the
    caller must handle the final completion object separately. Prefer
    :func:`call_llm` when tools are in use.

    Raises:
        openai.APIError: On API errors (connection, auth, rate limit, etc).
    """
    client = OpenAI(
        base_url=config.base_url,
        api_key=api_key or "none",
        timeout=config.timeout,
    )

    resolved_temperature = config.temperature if temperature is None else temperature
    resolved_max_tokens = config.max_tokens if max_tokens is None else max_tokens
    resolved_stop = config.stop if stop is None else stop

    # Build kwargs dynamically to avoid None values
    kwargs: dict = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            *messages,
        ],
        "temperature": resolved_temperature,
        "stream": True,
    }

    if resolved_max_tokens is not None:
        kwargs["max_tokens"] = resolved_max_tokens
    if resolved_stop:
        kwargs["stop"] = resolved_stop
    if response_format is not None:
        kwargs["response_format"] = response_format
    if tools is not None:
        kwargs["tools"] = tools

    stream = client.chat.completions.create(**kwargs)

    for chunk in stream:
        # Extract content defensively without calling mapping methods on
        # arbitrary objects (MagicMock implements .get and would confuse
        # the fallback path). Prefer attribute-style access for realistic
        # SDK objects, fall back to mapping-style only for plain dicts.
        content = None

        # Attribute-style (common for SDK MagicMock in tests and real clients)
        choices = getattr(chunk, "choices", None)
        if choices:
            try:
                first = choices[0]
                delta = getattr(first, "delta", None)
                if delta is not None:
                    content = getattr(delta, "content", None)
                    if content is None and isinstance(delta, dict):
                        content = delta.get("content")
            except Exception:
                content = None

        # Mapping-style fallback for real dict-like chunks
        if content is None and isinstance(chunk, dict):
            try:
                choices = chunk.get("choices", [])
                first = choices[0] if choices else {}
                delta = first.get("delta", {})
                if isinstance(delta, dict):
                    content = delta.get("content")
            except Exception:
                content = None

        if content:
            yield content
