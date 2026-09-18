# Routing Protocol

OpenJarvis orchestrates multiple language models using simple text routing tags embedded in model responses.

---

## Overview

Every prompt enters through the `generalist` router. The generalist determines whether the task can be answered directly or if it should be delegated to a domain specialist:

```text
User Input
    │
    ▼
┌───────────────────────────────┐
│     Generalist (Router)       │  Decides: Direct answer or specialist?
└───────────────────────────────┘
    │                       │
    ▼                       ▼
[ROUTE: return]     [ROUTE: math] / [ROUTE: code] / etc.
(Direct Answer)             │
                            ▼
                    ┌──────────────────────────────┐
                    │    Domain Specialist(s)      │  Executes task & calls tools
                    └──────────────────────────────┘
                            │
                            ▼
                    [RETURN] or [DELEGATE: <peer>]
                            │
                            ▼
                    Generalist synthesizes final answer
```

---

## Routing Tags

### Generalist Routing Tags

The generalist uses routing tags to direct flow:

| Tag | Purpose |
| :--- | :--- |
| `[ROUTE: return]` | Return the generated response directly to the user |
| `[ROUTE: math]` | Route the query to the `math` specialist |
| `[ROUTE: code]` | Route the query to the `code` specialist |
| `[ROUTE: knowledge]` | Route the query to the `knowledge` specialist |
| `[ROUTE: <specialist>]` | Route to any configured specialist matching `<specialist>` |

### Specialist Return & Delegation Tags

Specialists communicate using return and delegation tags:

| Tag | Purpose |
| :--- | :--- |
| `[RETURN]` | Conclude the specialist's work and return context to the generalist |
| `[DELEGATE: <specialist>]` | Hand off intermediate results to another specialist (must be in `delegates_to`) |

---

## Automatic Tag Stripping

All routing tags (`[ROUTE: ...]`, `[RETURN]`, `[DELEGATE: ...]`) are parsed and stripped by OpenJarvis before displaying the output to you. Your terminal displays only the clean synthesized answer.

---

## Tool Invocation During Routing

Specialists and the generalist have direct access to OpenJarvis's 49 built-in tools via OpenAI function calling schemas. When a tool is triggered:

1. The model issues a structured tool call (e.g. `evaluate_expression`, `search_web`).
2. OpenJarvis executes the tool locally.
3. The tool output is supplied back to the model.
4. The model incorporates the output and concludes with `[RETURN]`.

---

## Hop Limits (`max_hops`)

To prevent endless loops, OpenJarvis enforces a configurable hop limit (default: 10 hops, set by `max_hops: 10` in `specialists.yaml`). If a query reaches the maximum hop count, OpenJarvis halts further delegation and formats the best available response.

---

## Example Routing Walkthrough

```text
oj> Calculate 25% of 640 and write a Python one-liner to verify it

  ↳ routing: generalist → math
  ⚙ tool: evaluate_expression {"expression": "0.25 * 640"}
    → 160.0
  ↳ routing: math → code

25% of 640 is **160.0**.

Here is a Python one-liner to verify:
```python
assert 0.25 * 640 == 160.0
```
```

---

## See Also

- [Specialists Configuration](../configuration/specialists.md) — Configuring system prompts and delegation
- [Built-in Tools Reference](../tools/overview.md) — Full list of available tools
- [CLI Reference](cli.md) — Terminal commands and shortcut keys
