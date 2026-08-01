import json
from collections.abc import Iterator

import httpx

from openjarvis.types import SpecialistConfig


def _build_request(
    messages: list[dict],
    config: SpecialistConfig,
    api_key: str | None,
    stream: bool,
    temperature: float | None,
    max_tokens: int | None,
    stop: list[str] | None,
    response_format: dict | None,
) -> tuple[str, dict, dict]:
    """Assemble (url, headers, payload) for an OpenAI-compatible chat call."""
    url = f"{config.base_url.rstrip('/')}/chat/completions"

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            *messages,
        ],
        "temperature": config.temperature if temperature is None else temperature,
    }
    if stream:
        payload["stream"] = True

    resolved_max_tokens = config.max_tokens if max_tokens is None else max_tokens
    if resolved_max_tokens is not None:
        payload["max_tokens"] = resolved_max_tokens

    resolved_stop = config.stop if stop is None else stop
    if resolved_stop:
        payload["stop"] = resolved_stop

    if response_format is not None:
        payload["response_format"] = response_format

    return url, headers, payload


def call_llm(
    messages: list[dict],
    config: SpecialistConfig,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stop: list[str] | None = None,
    response_format: dict | None = None,
) -> str:
    """Call an OpenAI-compatible LLM API and return the full response text.

    Args:
        messages: Message dicts with "role" and "content". Roles must already be
            valid API roles -- translation from internal speaker names happens in
            the conductor, not here.
        config: SpecialistConfig supplying base_url, model, and the defaults for
            every override below.
        api_key: Optional API key for Bearer authentication.
        temperature, max_tokens, stop, response_format: per-call overrides;
            None means "use the specialist's configured value".

    Raises:
        httpx.HTTPStatusError: On non-2xx response.
        httpx.RequestError: On connection or network errors.
    """
    url, headers, payload = _build_request(
        messages, config, api_key, False, temperature, max_tokens, stop, response_format
    )

    with httpx.Client(timeout=config.timeout) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def call_llm_stream(
    messages: list[dict],
    config: SpecialistConfig,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    stop: list[str] | None = None,
    response_format: dict | None = None,
) -> Iterator[str]:
    """Same as :func:`call_llm`, but yields content deltas as they arrive.

    Parses the OpenAI SSE format: lines prefixed ``data: ``, terminated by
    ``data: [DONE]``. Chunks without a content delta (role-only openers, finish
    markers) yield nothing rather than an empty string.
    """
    url, headers, payload = _build_request(
        messages, config, api_key, True, temperature, max_tokens, stop, response_format
    )

    with httpx.Client(timeout=config.timeout) as client, client.stream(
        "POST", url, headers=headers, json=payload
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            line = line.strip()
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                # A malformed chunk should not abort a response that is
                # otherwise streaming fine.
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            content = (choices[0].get("delta") or {}).get("content")
            if content:
                yield content
