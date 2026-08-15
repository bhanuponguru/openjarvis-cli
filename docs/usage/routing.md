# Routing Protocol

OpenJarvis uses simple text-based tags to route conversations between the generalist and specialists. This page explains exactly how routing works.

---

## Overview

Every message in OpenJarvis flows through the generalist first. The generalist reads the user's request and decides whether to answer directly or delegate to a specialist — by including a routing tag in its response.

```
User Input
    │
    ▼
┌─────────────────────┐
│  Generalist         │  Decides: answer or route?
└─────────────────────┘
    │           │
    ▼           ▼
[ROUTE: return] [ROUTE: math]
(answer user)  (delegate)
                │
                ▼
         ┌─────────────┐
         │  Specialist │  Does the work
         └─────────────┘
                │
                ▼
           [RETURN]
         (back to generalist)
                │
                ▼
         Generalist synthesizes
         and answers user
```

---

## Routing Tags

### Generalist Tags

The generalist uses these tags to control message flow:

| Tag | Meaning |
|-----|---------|
| `[ROUTE: return]` | Send this response directly to the user |
| `[ROUTE: math]` | Route to the math specialist |
| `[ROUTE: code]` | Route to the code specialist |
| `[ROUTE: knowledge]` | Route to the knowledge specialist |
| `[ROUTE: <name>]` | Route to any specialist named `<name>` in your config |

Tags must appear **on their own line** in the model's response.

### Specialist Tags

Specialists use these tags to return results:

| Tag | Meaning |
|-----|---------|
| `[RETURN]` | Return this response to whoever called this specialist |
| `[DELEGATE: math]` | Delegate to the math specialist (requires `delegates_to` config) |
| `[DELEGATE: tool_use]` | Delegate to the tool_use specialist |
| `[DELEGATE: <name>]` | Delegate to any allowed specialist |

---

## Tag Stripping

All routing tags are automatically removed before the response reaches you. You never see raw tags like `[ROUTE: return]` or `[RETURN]` in the final output.

```
Model response (internal):
  "The answer is 42.
  [ROUTE: return]"

What you see:
  "The answer is 42."
```

---

## Routing Examples

### Simple: No Routing

For a simple question, the generalist answers directly:

```
> What is the speed of light?

(no routing indicators shown)

The speed of light in a vacuum is approximately 299,792,458 meters per second, or about 3 × 10⁸ m/s.
```

Internally, the generalist responded with `[ROUTE: return]`, so the answer went straight to you.

### Single Hop

```
> Solve for x: 2x + 10 = 20

  ↳ routing: generalist → math
  ↳ routing: math → generalist

x = 5. Subtracting 10 from both sides gives 2x = 10, then dividing by 2 gives x = 5.
```

The generalist routed to math, math solved it and returned, generalist delivered the answer.

### Multi-Hop with Tools

```
> What is 15% of Japan's current GDP?

  ↳ routing: generalist → knowledge
  ↳ routing: knowledge → tool_use
  ⚙ tool: search_web
    → Japan GDP approximately $4.2 trillion...
  ↳ routing: tool_use → knowledge
  ↳ routing: knowledge → math
  ↳ routing: math → tool_use
  ⚙ tool: evaluate_expression
    → 630000000000.0
  ↳ routing: tool_use → math
  ↳ routing: math → generalist

15% of Japan's GDP (approximately $4.2 trillion) is $630 billion.
```

### Specialist Delegation

One specialist can delegate to another if allowed by `delegates_to`:

```
> Write Python code to compute prime numbers up to 1000 and time how long it takes

  ↳ routing: generalist → code
  ↳ routing: code → tool_use
  ⚙ tool: run_python
    → Primes found: 168 in 0.0023s
  ↳ routing: tool_use → code
  ↳ routing: code → math
  ↳ routing: math → generalist

Here's the prime sieve code: [code shown]
It found 168 primes up to 1000 in 2.3 milliseconds.
```

---

## Configuring Routing

### Generalist System Prompt

The generalist must know which specialists are available and when to use them:

```yaml
generalist:
  system_prompt: |
    You are OpenJarvis.
    
    Route requests to specialists when appropriate:
    [ROUTE: return]     — Answer directly
    [ROUTE: math]       — Calculations, equations, proofs
    [ROUTE: code]       — Programming, debugging, code review
    [ROUTE: knowledge]  — Facts, research, explanations
    
    Always end with one routing tag. Never include multiple routing tags.
```

### Specialist Return Instructions

Every specialist must know to return results:

```yaml
specialists:
  math:
    system_prompt: |
      You are a math specialist. Solve problems step-by-step.
      When done, end with [RETURN] on its own line.
```

Without `[RETURN]`, the specialist's response sits silently and no further routing happens.

### Delegation Graph

Control which specialists can delegate to each other:

```yaml
specialists:
  code:
    delegates_to: ["math", "tool_use"]   # code can delegate to math and tool_use

  math:
    delegates_to: ["tool_use"]           # math can only delegate to tool_use

  knowledge:
    delegates_to: ["tool_use"]

  tool_use:
    delegates_to: []                     # tool_use always returns to caller
```

A specialist that tries `[DELEGATE: <name>]` for a specialist not in its `delegates_to` list will have the tag ignored — it will be treated as part of the response text instead.

---

## Routing Depth Limit

To prevent infinite loops, OpenJarvis limits routing to **20 hops** per conversation turn. If a conversation reaches 20 routing steps, it stops and returns whatever the current specialist has produced.

In practice, well-configured specialist prompts produce clean routing chains of 2-6 hops.

---

## Troubleshooting Routing

**Specialist not being used:**
Check that the generalist's system prompt includes `[ROUTE: specialist_name]` instructions and the specialist name matches exactly.

**Routing loops (same specialists called repeatedly):**
Ensure each specialist's prompt includes a clear `[RETURN]` instruction. Vague prompts can cause specialists to keep delegating instead of returning.

**No routing at all:**
If the generalist always answers directly, its system prompt may be too focused on direct responses. Add explicit routing instructions.

**Tags appearing in output:**
This shouldn't happen with proper configuration. If you see raw `[ROUTE: ...]` or `[RETURN]` in responses, the model may not be following the system prompt — try a more capable model or clearer instructions.

---

## See Also

- [Specialists Configuration](../configuration/specialists.md) — Set up routing prompts
- [Command Line](cli.md) — Using the CLI
- [Troubleshooting](../troubleshooting.md) — Routing issues
