# Math Tools

OpenJarvis includes 4 math tools for safe calculation, equation solving, unit conversion, and factorization.

---

## Tools

### `evaluate_expression`

Safely evaluate a mathematical expression. Uses AST validation — no `eval()` or code execution.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `expression` | string | yes | Math expression to evaluate |

**Supported operations:** `+`, `-`, `*`, `/`, `**` (power), `%` (modulo), parentheses, `abs()`, `round()`, `min()`, `max()`, `sum()`

**Returns:** Numeric result as a string.

**Example prompts:**
```
> Calculate 15% of Japan's GDP of 4.2 trillion
> What is 2 to the power of 32?
> Calculate (125 * 48) / 3 + 1000
```

---

### `solve_equation`

Solve a polynomial or linear equation symbolically for a variable.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `equation` | string | required | Equation as a string (e.g. `"2x + 5 = 15"`) |
| `variable` | string | `"x"` | Variable to solve for |

**Returns:** Solution(s) as a string.

**Example prompts:**
```
> Solve 2x + 5 = 15 for x
> Find the roots of x^2 - 5x + 6 = 0
> Solve 3y - 9 = 0 for y
```

---

### `convert_units`

Convert a value between common units.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `value` | number | yes | Value to convert |
| `from_unit` | string | yes | Source unit |
| `to_unit` | string | yes | Target unit |

**Supported conversions:**

| Category | Units |
|----------|-------|
| Distance | `m` ↔ `km`, `ft` ↔ `m`, `mi` ↔ `km` |
| Weight | `kg` ↔ `lb` |
| Temperature | `c` ↔ `f` |

**Returns:** Converted value as a string.

**Example prompts:**
```
> Convert 100 kilometers to miles
> How many pounds is 75 kilograms?
> What is 37 degrees Celsius in Fahrenheit?
> Convert 5280 feet to meters
```

---

### `prime_factorize`

Factorize a positive integer into its prime factors.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `n` | integer | yes | Positive integer to factorize |

**Returns:** List of prime factors.

**Example prompts:**
```
> What are the prime factors of 360?
> Factorize 1024
> Find the prime factorization of 100
```

---

## Usage Examples

### Arithmetic

```
> How much is a 20% tip on a $85 restaurant bill?

  ↳ routing: generalist → math → tool_use
  ⚙ tool: evaluate_expression
    → 17.0
  ↳ routing: tool_use → math → generalist

A 20% tip on an $85 bill is $17.00.
```

### Unit Conversion

```
> I need to run a 10K race. How many miles is that?

  ↳ routing: generalist → math → tool_use
  ⚙ tool: convert_units
    → 6.2137...
  ↳ routing: tool_use → math → generalist

A 10K race is approximately 6.21 miles.
```

### Equation Solving

```
> Solve for x: 3x + 12 = 0

  ↳ routing: generalist → math → tool_use
  ⚙ tool: solve_equation
    → x = -4
  ↳ routing: tool_use → math → generalist

The solution is x = -4.
```

---

## Tool Access Requirements

Math tools require the `tool_use` specialist:

```yaml
specialists:
  math:
    delegates_to: ["tool_use"]   # Required

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "..."
    model: "..."
```

---

## Safety

`evaluate_expression` validates the expression before evaluation — it cannot execute arbitrary code, access files, or make network requests. Only mathematical operations are permitted.

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [Date & Time Tools](datetime.md) — Date calculations
- [Text Processing](text.md) — Parsing and transformation
