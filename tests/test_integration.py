"""Integration tests checking outbound LangChain messages and multi-hop routing."""

from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, BaseMessage

from openjarvis.conductor import Conductor
from openjarvis.model_types import ConductorConfig, SpecialistConfig

VALID_API_ROLES = {"system", "user", "assistant", "tool", "human", "ai"}

def make_config(max_hops: int = 10) -> ConductorConfig:
    return ConductorConfig(
        generalist=SpecialistConfig(name="generalist", system_prompt="you are openjarvis"),
        specialists={
            "math": SpecialistConfig(
                name="math", system_prompt="math expert", delegates_to=["tool_use"]
            ),
            "tool_use": SpecialistConfig(name="tool_use", system_prompt="tools"),
        },
        max_hops=max_hops,
    )


class RecordingChatModel:
    """Stands in for LangChain BaseChatModel, capturing every message list and replaying scripted replies."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.invocations: list[list[BaseMessage]] = []

    def invoke(self, messages: list[BaseMessage], **kwargs):
        self.invocations.append(messages)
        content = self.replies.pop(0) if self.replies else "done\n[ROUTE: return]"
        return AIMessage(content=content)

    def stream(self, messages: list[BaseMessage], **kwargs):
        self.invocations.append(messages)
        content = self.replies.pop(0) if self.replies else "done\n[ROUTE: return]"
        parts = content.split(" ")
        for i, part in enumerate(parts):
            if i > 0:
                part = " " + part
            yield AIMessage(content=part)

    def bind_tools(self, tools, **kwargs):
        return self


@pytest.fixture
def transport():
    def install(replies):
        recorder = RecordingChatModel(replies)
        return recorder

    return install


def test_every_outbound_role_is_api_valid(transport):
    recorder = transport([
        "let me ask math\n[ROUTE: math]",
        "the answer is 42\n[RETURN]",
        "It is 42.\n[ROUTE: return]",
    ])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config())
        list(conductor.chat("what is 6*7?"))

    assert len(recorder.invocations) == 3, "expected generalist -> math -> generalist"
    for messages in recorder.invocations:
        for msg in messages:
            assert msg.type in VALID_API_ROLES, f"invalid role: {msg.type}"


def test_speaker_identity_is_preserved_in_context(transport):
    recorder = transport([
        "asking math\n[ROUTE: math]",
        "42\n[RETURN]",
        "It is 42.\n[ROUTE: return]",
    ])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config())
        list(conductor.chat("what is 6*7?"))

    final_messages = recorder.invocations[-1]
    system_contents = [m.content for m in final_messages if m.type == "system"]
    assert any("generalist" in str(c) for c in system_contents)
    assert any("math" in str(c) for c in system_contents)


def test_hop_cap_terminates_with_a_real_answer(transport):
    recorder = transport([
        "going to math\n[ROUTE: math]",
        "done\n[RETURN]",
        "Final answer.\n[ROUTE: return]",
    ])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config(max_hops=2))
        events = list(conductor.chat("loop please"))

    finals = [e for e in events if e["type"] == "final"]
    assert len(finals) == 1
    assert finals[0]["content"] == "Final answer."
    assert len(recorder.invocations) == 3


def test_generalist_self_route_does_not_spin(transport):
    recorder = transport(["thinking\n[ROUTE: generalist]"])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config())
        events = list(conductor.chat("hi"))

    assert len(recorder.invocations) == 1
    assert [e["type"] for e in events] == ["error", "final"]
    assert events[-1]["content"] == "thinking"


def test_chat_stream_hides_the_routing_tag(transport):
    recorder = transport(["The answer is 42.\n[ROUTE: return]"])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config())
        out = "".join(conductor.chat_stream("q"))

    assert "ROUTE" not in out
    assert out.strip() == "The answer is 42."


def test_chat_stream_emits_bracketed_prose(transport):
    recorder = transport(["See\n[note] this counts.\n[ROUTE: return]"])

    with patch("openjarvis.conductor.create_chat_model", return_value=recorder):
        conductor = Conductor(config=make_config())
        out = "".join(conductor.chat_stream("q"))

    assert "[note] this counts." in out
