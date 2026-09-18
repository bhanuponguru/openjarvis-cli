# Date & Time Tools

OpenJarvis includes 4 date and time tools for getting the current time, doing date arithmetic, formatting dates, and calculating durations.

---

## Tools

### `get_current_datetime`

Get the current date and time in any timezone.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `timezone` | string | `"UTC"` | Timezone name (e.g. `"America/New_York"`, `"Asia/Tokyo"`) |

**Returns:** ISO 8601 timestamp with weekday name.

**Example prompts:**
```
> What time is it right now?
> What's the current time in Tokyo?
> What day of the week is it in New York?
> What time is it in London?
```

**Common timezones:**
- `UTC`
- `America/New_York`
- `America/Chicago`
- `America/Los_Angeles`
- `Europe/London`
- `Europe/Paris`
- `Asia/Tokyo`
- `Asia/Shanghai`
- `Australia/Sydney`

---

### `date_arithmetic`

Add or subtract days and hours from a date.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `date_str` | string | required | Starting date/datetime (ISO format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`) |
| `days` | integer | `0` | Days to add (negative to subtract) |
| `hours` | integer | `0` | Hours to add (negative to subtract) |

**Returns:** Resulting datetime as ISO 8601 string.

**Example prompts:**
```
> What date is 30 days from today?
> My subscription started on 2024-01-15. When does it expire after 1 year?
> What was the date 90 days ago?
> Add 2 weeks to 2024-08-01
```

---

### `format_datetime`

Format a date string in a human-readable format.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_str` | string | yes | Date string (ISO format) |
| `fmt` | string | yes | Output format string (Python strftime) |

**Returns:** Formatted date string.

**Common format strings:**

| Format | Example Output |
|--------|---------------|
| `%B %d, %Y` | August 15, 2026 |
| `%d/%m/%Y` | 15/08/2026 |
| `%m/%d/%Y` | 08/15/2026 |
| `%A, %B %d` | Saturday, August 15 |
| `%Y-%m-%d` | 2026-08-15 |
| `%I:%M %p` | 02:30 PM |

**Example prompts:**
```
> Format 2026-08-15 as "August 15, 2026"
> Display the date 2024-12-25 in European format (DD/MM/YYYY)
> Show 2024-03-14T15:00:00 in a readable format
```

---

### `days_between`

Calculate the number of days between two dates.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `date_a` | string | yes | First date (ISO format: `YYYY-MM-DD`) |
| `date_b` | string | yes | Second date (ISO format: `YYYY-MM-DD`) |

**Returns:** Number of days between the dates (positive integer, order doesn't matter).

**Example prompts:**
```
> How many days until Christmas (December 25)?
> How long has it been since 2024-01-01?
> How many days between my birthday on March 15 and the end of the year?
> How many days is a 90-day trial that started on 2024-06-01?
```

---

## Usage Examples

### Current Time in Timezone

```text
oj> What time is it in Sydney right now?

  ↳ routing: generalist → knowledge
  ⚙ tool: get_current_datetime {"timezone": "Australia/Sydney"}
    → 2026-08-16T06:45:12 Sunday

It is currently **6:45 AM on Sunday, August 16** in Sydney, Australia.
```

### Deadline & Days Between

```text
oj> My project deadline is 2026-09-30. How many days from 2026-08-15 is that?

  ↳ routing: generalist → math
  ⚙ tool: days_between {"date_a": "2026-08-15", "date_b": "2026-09-30"}
    → 46

There are **46 days** remaining until September 30.
```

---

## See Also

- [Tools Overview](overview.md) — All 49 built-in tools
- [Math Tools](math.md) — Arithmetic and calculations
- [Data Processing](data.md) — JSON and text manipulations
