from openjarvis.conductor import _stream_without_tag


def collect_emitted(deltas):
    emitted = []
    for _delta, emit in _stream_without_tag(iter(deltas)):
        if emit:
            emitted.append(emit)
    return "".join(emitted)


def test_tag_split_across_chunks_is_withheld():
    deltas = ["I will check\n", "[RO", "UTE: math]"]
    assert collect_emitted(deltas) == "I will check\n"


def test_bracketed_prose_at_line_start_released_if_not_tag():
    deltas = ["[note] this", " is fine\n"]
    assert collect_emitted(deltas) == "[note] this is fine\n"


def test_incomplete_tag_at_end_of_stream_is_suppressed():
    deltas = ["Hello\n", "[ROUTE: ma"]
    assert collect_emitted(deltas) == "Hello\n"
