from openjarvis.parser import is_route_tag, parse_route_tag


def test_generalist_return():
    content, route = parse_route_tag("Hello!\n[ROUTE: return]")
    assert content.strip() == "Hello!"
    assert route == "return"


def test_generalist_route_to_specialist():
    content, route = parse_route_tag("Let me check\n[ROUTE: math]")
    assert content.strip() == "Let me check"
    assert route == "math"


def test_specialist_return():
    content, route = parse_route_tag("42\n[RETURN]")
    assert content.strip() == "42"
    assert route == "return"


def test_specialist_delegate():
    content, route = parse_route_tag("I need help\n[DELEGATE: math]")
    assert content.strip() == "I need help"
    assert route == "math"


def test_no_tag_defaults_to_return():
    """A model that forgets the protocol must still terminate the loop."""
    content, route = parse_route_tag("Just a normal response")
    assert content == "Just a normal response"
    assert route == "return"


def test_last_tag_wins():
    """Models often restate a plan mid-response before committing at the end."""
    _, route = parse_route_tag("First\n[ROUTE: math]\nSecond\n[ROUTE: code]")
    assert route == "code"


def test_tag_mid_prose_is_not_a_route():
    """Tags must be on their own line, as every system prompt instructs.

    Unanchored patterns matched here, so a model writing about delegation
    triggered a real delegation it never intended -- and the surrounding
    sentence was silently mangled by the tag-stripping.
    """
    text = "I could use [DELEGATE: math] here, but I'll answer directly."
    content, route = parse_route_tag(text)
    assert route == "return"
    assert content == text


def test_tag_with_surrounding_whitespace_still_parses():
    _, route = parse_route_tag("Hello\n   [ROUTE: math]   \n")
    assert route == "math"


def test_case_insensitive():
    _, route = parse_route_tag("Hello\n[route: return]")
    assert route == "return"


def test_generalist_delegate_tag_still_parses():
    """The parser is format-agnostic; the conductor decides what is permitted."""
    _, route = parse_route_tag("Hi\n[DELEGATE: math]")
    assert route == "math"


def test_route_tag_with_spaces():
    _, route = parse_route_tag("Hello\n[ROUTE:  math  ]")
    assert route == "math"


def test_is_route_tag_distinguishes_tag_from_absence():
    """parse_route_tag's "return" is ambiguous: found-a-tag vs. defaulted.

    Streaming needs to tell those apart to decide whether to show the text.
    """
    assert is_route_tag("[ROUTE: return]")
    assert is_route_tag("  [RETURN]  ")
    assert is_route_tag("[DELEGATE: math]")
    assert not is_route_tag("The answer is 42.")
    assert not is_route_tag("")
    assert not is_route_tag("[note] a bracketed aside")
    # A tag with prose attached is not a bare tag, so it must stay visible.
    assert not is_route_tag("Sure thing [ROUTE: math]")


def test_tag_with_crlf_line_endings():
    """Windows-style CRLF from LLM endpoints should parse correctly."""
    content, route = parse_route_tag("Hello world\r\n[ROUTE: math]\r\n")
    assert content.strip() == "Hello world"
    assert route == "math"

    content_ret, route_ret = parse_route_tag("Done\r\n[RETURN]\r\n")
    assert content_ret.strip() == "Done"
    assert route_ret == "return"
