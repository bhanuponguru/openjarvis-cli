"""Integration tests that patch the OpenAI SDK, not `call_llm`.

Every existing conductor test monkeypatches `call_llm` wholesale, so the request
payload is never built; every provider test hands `call_llm` pre-made messages,
so real conversation history never reaches it. The role bug -- internal speaker
names like "generalist" and "math" going out as API roles, which every
OpenAI-compatible server rejects with HTTP 400 -- lived exactly in that gap.

These tests close it by asserting on what would actually go over the wire.
"""

from unittest.mock import MagicMock

import pytest

from openjarvis.conductor import Conductor
from openjarvis.types import ConductorConfig, SpecialistConfig

VALID_API_ROLES = {"system", "user", "assistant", "tool"}


def make_config(max_hops: int = 10) -> ConductorConfig:
    return ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="you are jarvis"),
        specialists={
            "math": SpecialistConfig(
                name="math", system_prompt="math expert", delegates_to=["tool_use"]
            ),
            "tool_use": SpecialistConfig(name="tool_use", system_prompt="tools"),
        },
        max_hops=max_hops,
    )


class RecordingOpenAI:
    """Stands in for OpenAI client, capturing every payload and replaying scripted replies."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.payloads: list[dict] = []
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = self._create

    def _create(self, **kwargs):
        # Reconstruct the payload dict for inspection
        payload = {k: v for k, v in kwargs.items() if v is not None and k != "stream"}
        self.payloads.append(payload)

        content = self.replies.pop(0) if self.replies else "done\n[ROUTE: return]"

        if kwargs.get("stream", False):
            # Return a stream iterator
            return self._make_stream(content)
        else:
            # Return a completion object
            mock_completion = MagicMock()
            mock_completion.choices[0].message.content = content
            return mock_completion

    def _make_stream(self, content: str):
        """Create a stream iterator for streaming responses."""
        # Split content into chunks on spaces for more realistic streaming
        parts = content.split(" ")
        for i, part in enumerate(parts):
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            if i > 0:
                part = " " + part
            chunk.choices[0].delta.content = part
            yield chunk

        # Final chunk with no content (finish marker)
        final_chunk = MagicMock()
        final_chunk.choices = [MagicMock()]
        final_chunk.choices[0].delta.content = None
        yield final_chunk


@pytest.fixture
def transport(monkeypatch):
    def install(replies):
        recorder = RecordingOpenAI(replies)
        monkeypatch.setattr("openjarvis.providers.OpenAI", lambda **kwargs: recorder)
        return recorder

    return install


# ---------------------------------------------------------------------------
# The role bug
# ---------------------------------------------------------------------------

def test_every_outbound_role_is_api_valid(transport):
    """THE regression test: a multi-hop chat must never send an invalid role.

    Before the fix, hop 2 carried {"role": "generalist"} and every real backend
    answered HTTP 400. No mocked test could see it.
    """
    recorder = transport([
        "let me ask math\n[ROUTE: math]",
        "the answer is 42\n[RETURN]",
        "It is 42.\n[ROUTE: return]",
    ])

    conductor = Conductor(config=make_config())
    list(conductor.chat("what is 6*7?"))

    assert len(recorder.payloads) == 3, "expected generalist -> math -> generalist"
    for payload in recorder.payloads:
        for msg in payload["messages"]:
            assert msg["role"] in VALID_API_ROLES, f"invalid role: {msg['role']}"


def test_speaker_identity_is_preserved_in_content(transport):
    """Mapping to `assistant` must not erase who said what."""
    recorder = transport([
        "asking math\n[ROUTE: math]",
        "42\n[RETURN]",
        "It is 42.\n[ROUTE: return]",
    ])

    conductor = Conductor(config=make_config())
    list(conductor.chat("what is 6*7?"))

    final_messages = recorder.payloads[-1]["messages"]
    assistant_content = [m["content"] for m in final_messages if m["role"] == "assistant"]
    assert any(c.startswith("[generalist]:") for c in assistant_content)
    assert any(c.startswith("[math]:") for c in assistant_content)


def test_user_and_system_roles_pass_through_unprefixed(transport):
    """Only model turns get the [speaker] prefix; user text must stay verbatim."""
    recorder = transport(["hi\n[ROUTE: return]"])

    conductor = Conductor(config=make_config())
    list(conductor.chat("hello there"))

    user_msgs = [m for m in recorder.payloads[0]["messages"] if m["role"] == "user"]
    assert [m["content"] for m in user_msgs] == ["hello there"]


def test_system_prompt_is_the_callees_own(transport):
    """Each hop must be given ITS system prompt, not the previous speaker's."""
    recorder = transport([
        "routing\n[ROUTE: math]",
        "42\n[RETURN]",
        "42.\n[ROUTE: return]",
    ])

    conductor = Conductor(config=make_config())
    list(conductor.chat("q"))

    assert recorder.payloads[0]["messages"][0]["content"] == "you are jarvis"
    assert recorder.payloads[1]["messages"][0]["content"] == "math expert"


# ---------------------------------------------------------------------------
# Loop safety
# ---------------------------------------------------------------------------

def test_hop_cap_terminates_with_a_real_answer(transport):
    """A ping-pong loop must stop at max_hops and still answer the user."""
    # Exactly max_hops routing replies, then the reply to the forced final call.
    recorder = transport(
        ["route\n[ROUTE: math]", "back\n[RETURN]"] * 2 + ["Final answer.\n[ROUTE: return]"]
    )

    conductor = Conductor(config=make_config(max_hops=4))
    events = list(conductor.chat("loop please"))

    finals = [e for e in events if e["type"] == "final"]
    assert len(finals) == 1
    assert finals[0]["content"] == "Final answer."
    # 4 capped hops + 1 forced final call.
    assert len(recorder.payloads) == 5

    last_messages = recorder.payloads[-1]["messages"]
    assert any("Hop limit reached" in m["content"] for m in last_messages)


def test_generalist_self_route_does_not_spin(transport):
    """[ROUTE: generalist] from the generalist makes no progress; treat as final."""
    recorder = transport(["thinking\n[ROUTE: generalist]"])

    conductor = Conductor(config=make_config())
    events = list(conductor.chat("hi"))

    assert len(recorder.payloads) == 1, "must not call the generalist again"
    assert [e["type"] for e in events] == ["error", "final"]
    assert events[-1]["content"] == "thinking"


# ---------------------------------------------------------------------------
# Per-call parameters
# ---------------------------------------------------------------------------

def test_max_tokens_and_stop_reach_the_payload(transport):
    recorder = transport(["hi\n[ROUTE: return]"])

    config = make_config()
    config.generalist.max_tokens = 256
    config.generalist.stop = ["\n\n"]

    list(Conductor(config=config).chat("hi"))

    assert recorder.payloads[0]["max_tokens"] == 256
    assert recorder.payloads[0]["stop"] == ["\n\n"]


def test_unset_optional_params_are_omitted(transport):
    """Sending max_tokens: null breaks strict servers -- omit rather than null."""
    recorder = transport(["hi\n[ROUTE: return]"])
    list(Conductor(config=make_config()).chat("hi"))

    # OpenAI SDK doesn't include None values in the payload
    assert "max_tokens" not in recorder.payloads[0] or recorder.payloads[0]["max_tokens"] is None
    assert "stop" not in recorder.payloads[0] or recorder.payloads[0]["stop"] is None


# ---------------------------------------------------------------------------
# SSE streaming
# ---------------------------------------------------------------------------

class StreamingOpenAI:
    """Mock OpenAI client for streaming tests with scripted SSE-like chunks."""

    def __init__(self, chunks: list[str | None]):
        self.chunks = chunks
        self.payloads: list[dict] = []
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = self._create

    def _create(self, **kwargs):
        payload = {k: v for k, v in kwargs.items() if v is not None and k != "stream"}
        self.payloads.append(payload)

        # Return iterator of chunks
        for content in self.chunks:
            chunk = MagicMock()
            chunk.choices = [MagicMock()] if content is not None else []
            if content is not None:
                chunk.choices[0].delta.content = content
            yield chunk


def test_stream_parses_sse_deltas(monkeypatch):
    # SDK handles delta parsing, so we just need content chunks
    chunks = [None, "Hello", None, " world", None, None]  # None = role-only or empty delta

    def make_client(**kwargs):
        return StreamingOpenAI(chunks)

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    from openjarvis.providers import call_llm_stream
    result = list(call_llm_stream([], config))

    assert result == ["Hello", " world"]


def test_stream_survives_a_malformed_chunk(monkeypatch):
    """The SDK handles malformed chunks internally, but we test that empty deltas are filtered."""
    chunks = ["Hello", None, " world", None]

    def make_client(**kwargs):
        return StreamingOpenAI(chunks)

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    from openjarvis.providers import call_llm_stream
    result = list(call_llm_stream([], config))

    assert result == ["Hello", " world"]


def test_chat_stream_hides_the_routing_tag(transport):
    """The user must never see [ROUTE: return], even split across chunks."""
    transport(["The answer is 42.\n[ROUTE: return]"])

    conductor = Conductor(config=make_config())
    out = "".join(conductor.chat_stream("q"))

    assert "ROUTE" not in out
    assert out.strip() == "The answer is 42."


def test_chat_stream_emits_bracketed_prose(transport):
    """Withholding must be provisional: non-tag bracketed text still reaches the user."""
    transport(["See\n[note] this counts.\n[ROUTE: return]"])

    conductor = Conductor(config=make_config())
    out = "".join(conductor.chat_stream("q"))

    assert "[note] this counts." in out


def test_chat_stream_calls_the_generalist_once(transport):
    """Streaming must not double-bill by re-issuing the final turn."""
    recorder = transport(["Hi.\n[ROUTE: return]"])

    conductor = Conductor(config=make_config())
    list(conductor.chat_stream("q"))

    assert len(recorder.payloads) == 1
