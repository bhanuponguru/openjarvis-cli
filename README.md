# OpenJarvis — the client

The client-side orchestrator. Routes a user's request across a generalist and a
team of specialists, all reached over an OpenAI-compatible HTTP API.

OpenJarvis is model-agnostic by construction: it depends only on `httpx` and
`pyyaml`, and nothing here knows whether the backend is
[jarvis](../jarvis/README.md), Ollama, or OpenAI.

```bash
uv run openjarvis
```

Configuration lives in `specialists.yaml` at the repo root (override with
`OJ_CONFIG`). See the [user guide](../../docs/openjarvis/user-guide.md).
