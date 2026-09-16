import re

# Tags must sit on their own line, which is what every system prompt in
# specialists.yaml instructs. Unanchored patterns match mid-prose, so a model
# writing "I'll use [DELEGATE: math] for this" would trigger a real delegation
# it never intended. `(?m)^\s*TAG\s*$` makes the documented contract enforced.
_ROUTE_PATTERN = re.compile(r"^[ \t]*\[ROUTE:\s*(\w+)\s*\][ \t]*$", re.IGNORECASE | re.MULTILINE)
_RETURN_PATTERN = re.compile(r"^[ \t]*\[RETURN\][ \t]*$", re.IGNORECASE | re.MULTILINE)
_DELEGATE_PATTERN = re.compile(r"^[ \t]*\[DELEGATE:\s*(\w+)\s*\][ \t]*$", re.IGNORECASE | re.MULTILINE)


def _find_last_match(response: str) -> tuple[re.Match | None, str | None]:
    """Find the last routing tag match across all patterns.

    Returns:
        (match, match_type) where match_type is "route", "return", or "delegate"
    """
    normalized = response.replace("\r\n", "\n")
    candidates: list[tuple[re.Match, str]] = []
    for m in _ROUTE_PATTERN.finditer(normalized):
        candidates.append((m, "route"))
    for m in _RETURN_PATTERN.finditer(normalized):
        candidates.append((m, "return"))
    for m in _DELEGATE_PATTERN.finditer(normalized):
        candidates.append((m, "delegate"))

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[0].start())
    return candidates[-1]


def is_route_tag(text: str) -> bool:
    """True if `text` is exactly one routing tag and nothing else.

    Distinct from ``parse_route_tag``, whose "return" result is ambiguous: it
    means both "[ROUTE: return] was found" and "no tag at all, defaulting".
    Streaming needs to tell those apart to know whether to show the text.
    """
    stripped = text.strip()
    if not stripped:
        return False
    return any(
        p.fullmatch(stripped)
        for p in (_ROUTE_PATTERN, _RETURN_PATTERN, _DELEGATE_PATTERN)
    )


def parse_route_tag(response: str) -> tuple[str, str | None]:
    """Parse the routing tag from an LLM response.

    Recognises ``[ROUTE: X]``, ``[RETURN]``, and ``[DELEGATE: X]``, each on its
    own line. When several appear, the last wins -- models often restate a plan
    mid-response before committing at the end.

    Args:
        response: The raw LLM response text.

    Returns:
        (cleaned_content, route_target). ``route_target`` is "return" when no
        tag is present, so a model that forgets the protocol still terminates.
    """
    normalized = response.replace("\r\n", "\n")
    match, match_type = _find_last_match(normalized)

    if match is None:
        return normalized.strip(), "return"

    route = "return" if match_type == "return" else match.group(1).strip().lower()

    cleaned = normalized[:match.start()] + normalized[match.end():]
    return cleaned.strip(), route
