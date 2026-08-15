from unittest.mock import MagicMock

from openjarvis.model_types import SpecialistConfig


def make_attr_completion(content: str):
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message = MagicMock()
    mock_completion.choices[0].message.content = content
    return mock_completion


def make_dict_completion(content: str):
    return {"choices": [{"message": {"content": content}}]}


def test_call_llm_handles_attribute_style(monkeypatch):
    from openjarvis.providers import call_llm

    def make_client(**kwargs):
        class C:
            def __init__(self):
                self.chat = MagicMock()
                self.chat.completions = MagicMock()
                self.chat.completions.create = lambda **k: make_attr_completion("hello")

        return C()

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    res = call_llm([], config)
    assert res == "hello"


def test_call_llm_handles_dict_style(monkeypatch):
    from openjarvis.providers import call_llm

    def make_client(**kwargs):
        class C:
            def __init__(self):
                self.chat = MagicMock()
                self.chat.completions = MagicMock()
                self.chat.completions.create = lambda **k: make_dict_completion("hi")

        return C()

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    res = call_llm([], config)
    assert res == "hi"


def test_call_llm_with_tools_returns_message_object(monkeypatch):
    from openjarvis.providers import call_llm

    def make_client(**kwargs):
        class C:
            def __init__(self):
                self.chat = MagicMock()
                self.chat.completions = MagicMock()

            def _create(self, **k):
                comp = MagicMock()
                comp.choices = [MagicMock()]
                comp.choices[0].message = {"content": "toolcall", "tool_calls": []}
                return comp

            def chat_completions_create(self, **k):
                return self._create(**k)

        inst = C()
        inst.chat.completions.create = inst._create
        return inst

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    res = call_llm([], config, tools=[{"type": "function"}])
    # When tools are supplied, expect a message-like object (dict or object)
    assert isinstance(res, (dict, MagicMock))


def test_call_llm_stream_with_tools_yields_content_chunks(monkeypatch):
    # When tools are supplied, text content chunks are still yielded; only
    # tool-call-only deltas (no text) are suppressed.
    class StreamingOpenAI:
        def __init__(self, chunks):
            self.chunks = chunks
            self.chat = MagicMock()
            self.chat.completions = MagicMock()
            self.chat.completions.create = self._create

        def _create(self, **kwargs):
            for c in self.chunks:
                chunk = MagicMock()
                chunk.choices = [MagicMock()]
                chunk.choices[0].delta.content = c
                yield chunk

    def make_client(**kwargs):
        return StreamingOpenAI(["Hello", " world"])

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    from openjarvis.providers import call_llm_stream
    out = list(call_llm_stream([], config, tools=[{"type": "function"}]))
    # Content chunks are passed through; tool-call-only (no content) chunks are skipped.
    assert out == ["Hello", " world"]


def test_call_llm_stream_with_tools_skips_empty_chunks(monkeypatch):
    # Chunks with no content (tool-call deltas) must be suppressed.
    class StreamingOpenAI:
        def __init__(self, chunks):
            self.chunks = chunks
            self.chat = MagicMock()
            self.chat.completions = MagicMock()
            self.chat.completions.create = self._create

        def _create(self, **kwargs):
            for c in self.chunks:
                chunk = MagicMock()
                chunk.choices = [MagicMock()]
                chunk.choices[0].delta.content = c  # None → tool-call delta
                yield chunk

    def make_client(**kwargs):
        return StreamingOpenAI([None, None])  # pure tool-call chunks

    monkeypatch.setattr("openjarvis.providers.OpenAI", make_client)

    config = SpecialistConfig(name="g", system_prompt="p")
    from openjarvis.providers import call_llm_stream
    out = list(call_llm_stream([], config, tools=[{"type": "function"}]))
    assert out == []
