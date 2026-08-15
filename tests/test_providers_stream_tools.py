from unittest.mock import MagicMock

from openjarvis.model_types import SpecialistConfig


class StreamingOpenAI:
    def __init__(self, chunks):
        self.chunks = chunks
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = self._create

    def _create(self, **kwargs):
        for content in self.chunks:
            chunk = MagicMock()
            chunk.choices = [MagicMock()] if content is not None else []
            if content is not None:
                chunk.choices[0].delta = MagicMock()
                chunk.choices[0].delta.content = content
            yield chunk


def test_call_llm_stream_with_tools_yields_no_content(monkeypatch):
    # When `tools` is supplied the model may produce tool_calls rather than
    # streaming content. The stream should not crash and should yield no
    # textual deltas in this case; the caller is expected to handle the final
    # non-stream completion separately.
    chunks = [None, None]

    def make_client(**kwargs):
        return StreamingOpenAI(chunks)

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    from openjarvis.providers import call_llm_stream

    result = list(call_llm_stream([], config, tools=[{"type": "function"}]))
    assert result == []
