# First Steps with OpenJarvis

Now that OpenJarvis is installed and configured, let's explore how to make the most of your interactive assistant.

---

## Interactive Chat

Start an interactive session:

```bash
openjarvis
```

You will see the interactive prompt:

```text
OpenJarvis (type 'exit' or 'quit' to stop)

oj> 
```

Type your prompt and press `Enter`. OpenJarvis analyzes the task, selects appropriate specialists, runs any needed tools, and presents the synthesized result.

---

## Example Interactions

### 1. Mathematics & Calculation

```text
oj> Solve for x: 3*x + 15 = 45 and factorize the answer

  ↳ routing: generalist → math
  ⚙ tool: solve_equation {"equation": "3*x + 15 = 45", "variable": "x"}
    → "[10]"
  ⚙ tool: prime_factorize {"n": 10}
    → "[2, 5]"

For the equation `3x + 15 = 45`:
- Solving gives **x = 10**.
- The prime factorization of 10 is **2 × 5**.
```

### 2. Live Web Search & Factual Lookups

```text
oj> What are the primary features released in Python 3.13?

  ↳ routing: generalist → knowledge
  ⚙ tool: search_web {"query": "Python 3.13 key features release"}
    → [{"title": "What's New In Python 3.13", ...}]

Python 3.13 introduces several notable features:
1. An experimental free-threaded build (disabling the GIL).
2. A preliminary Just-In-Time (JIT) compiler.
3. Enhanced interactive REPL with multi-line editing and color support.
4. Improved error messages and typing improvements.
```

### 3. Software Engineering & Code Generation

```text
oj> Write a Python function to validate and format an email address

  ↳ routing: generalist → code

Here is a robust function to validate and normalize email addresses:

```python
import re

def normalize_email(email: str) -> str | None:
    """Validate and lower-case an email address. Returns None if invalid."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    email = email.strip()
    if re.match(pattern, email):
        return email.lower()
    return None
```
```

### 4. File Operations & Local Inspection

```text
oj> Read the first 10 lines of config.yaml

  ↳ routing: generalist → code
  ⚙ tool: read_file {"path": "config.yaml", "max_chars": 500}
    → "max_hops: 10\ngeneralist:\n..."

Here are the first lines of `config.yaml`:
```yaml
max_hops: 10
generalist:
  name: "generalist"
```
```

---

## Understanding Routing

When OpenJarvis processes a request, it displays real-time routing hops in dim text:

```text
  ↳ routing: generalist → math
  ⚙ tool: evaluate_expression {"expression": "..."}
  ↳ routing: math → code
```

- `↳ routing: generalist → <specialist>`: Indicates the generalist routed the task to a specialist.
- `⚙ tool: <name>`: Indicates a specialist called a built-in tool via function calling.
- `↳ routing: <specialist> → <specialist>`: Indicates approved delegation between specialists.

---

## Best Practices

1. **Ask in Natural Language**: You do not need special commands to trigger tools. The models recognize when calculations, web lookups, or file reads are required.
2. **Multi-line Editing**: Press `Escape` followed by `Enter` to create a new line before submitting.
3. **Session Notes**: You can ask OpenJarvis to remember information within a session:
   - *"Remember that my target deployment region is us-east-1"*
   - *"What deployment region did I specify earlier?"*
4. **Exit**: Type `exit`, `quit`, or press `Ctrl+D` to end the session.

---

## Next Steps

- **[Configuration Overview →](../configuration/overview.md)** — Customizing models and providers
- **[Built-in Tools Reference →](../tools/overview.md)** — Detailed parameters for all 49 tools
- **[Troubleshooting Guide →](../troubleshooting.md)** — Common questions and solutions
