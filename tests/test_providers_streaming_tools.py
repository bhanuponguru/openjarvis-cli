from openjarvis.model_types import SpecialistConfig


def test_stream_with_tools_yields_content_chunks(monkeypatch):
    """When tools are supplied, text content chunks are still streamed.

    Tool-call-only deltas (empty choices list) are suppressed, but chunks that
    carry actual text pass through so callers get a live stream even when the
    model may also make tool calls.
    """
    class StreamingOpenAI:
        def __init__(self, chunks):
            self.chunks = chunks
            self.chat = self
            self.completions = self

        def create(self, **kwargs):
            def _iter():
                for content in self.chunks:
                    chunk = type("C", (), {})()
                    if content is not None:
                        c = type("Delta", (), {})()
                        c.content = content
                        choice = type("Choice", (), {})()
                        choice.delta = c
                        chunk.choices = [choice]
                    else:
                        chunk.choices = []
                    yield chunk

            return _iter()

    chunks = ["hello", " world"]
    monkeypatch.setattr("openjarvis.providers.OpenAI", lambda **k: StreamingOpenAI(chunks))

    from openjarvis.providers import call_llm_stream

    config = SpecialistConfig(name="g", system_prompt="p")
    out = list(call_llm_stream([], config, tools=[{"type": "function"}]))
    # Content chunks must pass through; only empty-choices (tool-call) deltas are skipped.
    assert out == ["hello", " world"]


def test_stream_with_tools_skips_empty_choice_chunks(monkeypatch):
    """Tool-call-only deltas (empty choices) must be suppressed during streaming."""
    class StreamingOpenAI:
        def __init__(self, chunks):
            self.chunks = chunks
            self.chat = self
            self.completions = self

        def create(self, **kwargs):
            def _iter():
                for _content in self.chunks:
                    chunk = type("C", (), {})()
                    # None → empty choices → tool-call delta
                    chunk.choices = []
                    yield chunk

            return _iter()

    monkeypatch.setattr(
        "openjarvis.providers.OpenAI", lambda **k: StreamingOpenAI([None, None])
    )

    from openjarvis.providers import call_llm_stream

    config = SpecialistConfig(name="g", system_prompt="p")
    out = list(call_llm_stream([], config, tools=[{"type": "function"}]))
    assert out == []
