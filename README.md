# OpenJarvis — the client

The client-side orchestrator. Routes a user's request across a generalist and a team of specialists, all reached over an OpenAI-compatible HTTP API.

OpenJarvis is model-agnostic by construction: it never imports `jarvis` or `torch`. It works with any OpenAI-compatible backend — Ollama, OpenAI, Groq, OpenRouter, or the bundled `jarvis` inference server.

```bash
uv run openjarvis
# short alias:
uv run oj
```

Dependencies: `openai`, `pyyaml`, `rich`, `ddgs`, `pytz`.

Configuration lives in `specialists.yaml` at the repo root (override with `OJ_CONFIG`). See the [user guide](../../docs/user/openjarvis/index.md).
