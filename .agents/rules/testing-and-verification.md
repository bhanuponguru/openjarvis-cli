# Testing and Verification Guidelines — openjarvis-cli

## Testing Discipline
- All unit and integration tests live under `tests/`.
- Tests must execute on CPU without external network dependencies.
- HTTP-based tests (e.g. testing conductor streaming, provider endpoints) must use mocked HTTP fixtures (`respx`, custom httpx transports, or local unittest mocks).
- The complete test suite must execute in under 10 seconds.

## Mandatory Pre-Commit Checks
Before committing any code:
```bash
uv run ruff check .
uv run mypy
uv run pytest -q
```
All checks must pass with zero warnings or errors.

