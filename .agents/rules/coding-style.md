# Coding Style & Standards — openjarvis-cli

## Python Target & Conventions
- Target Python 3.13 / 3.14.
- 4-space indentation throughout.
- Public functions and classes require complete type annotations.
- Ruff linter rules:
  - `E`, `F` (Pyflakes / Pycodestyle)
  - `I` (isort import formatting)
  - `UP` (pyupgrade)
  - `B` (bugbear)
  - `SIM` (simplify)
- 100-character line length limit.

## Tool & Function Signatures
- Built-in tools must declare JSON-serializable parameters using standard Python type hints or Pydantic models.
- All tools must return structured text or dict payloads that format clearly in terminal UI output.
- Tools must fail gracefully with descriptive error messages rather than unhandled Python tracebacks.
