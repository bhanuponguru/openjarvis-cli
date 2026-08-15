from openjarvis.model_types import SpecialistConfig


def test_stream_with_tools_yields_nothing(monkeypatch):
    """When `tools` is supplied, the streaming call should not yield content.

    The model may return tool_calls instead of content; streaming should be
    suppressed so callers re-request the final completion via the non-streaming
    API and inspect `tool_calls`.
    """
    class StreamingOpenAI:
        def __init__(self, chunks):
            self.chunks = chunks
            self.chat = self
            self.completions = self

        def create(self, **kwargs):
            # Return iterator of chunks
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
    assert out == []
