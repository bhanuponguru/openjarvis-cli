# Text Processing Tools

OpenJarvis includes 5 text processing tools for parsing JSON, querying data, working with CSV, and applying regex.

---

## Tools

### `parse_json`

Parse and pretty-print a JSON string.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `json_str` | string | yes | JSON string to parse |

**Returns:** Indented, formatted JSON string. Returns an error message if the input is invalid JSON.

**Example prompts:**
```
> Parse and format this JSON: {"name":"Alice","age":30,"active":true}
> Pretty-print this API response: [paste minified JSON]
> Validate this JSON and show it formatted
```

---

### `jq_query`

Query a JSON string using dot-notation paths.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `json_str` | string | yes | JSON string to query |
| `path` | string | yes | Dot-notation path (e.g. `users.0.name`) |

**Returns:** Value at the path, or an error if not found.

**Path syntax:**

| Path | Accesses |
|------|---------|
| `name` | `{"name": "Alice"}` → `"Alice"` |
| `user.email` | `{"user": {"email": "..."}}` |
| `items.0` | First element of `items` array |
| `items.2.price` | `price` of third item |

**Example prompts:**
```
> Extract the email from this JSON: {"user": {"name": "Alice", "email": "alice@example.com"}}
> Get the first item's price from: {"items": [{"name": "Book", "price": 9.99}]}
> What is the status in this API response: [paste JSON]
```

---

### `parse_csv`

Parse a CSV string and display it as a readable table.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `csv_str` | string | required | CSV string to parse |
| `delimiter` | string | `","` | Field delimiter |

**Returns:** Markdown table showing the first 20 rows.

**Example prompts:**
```
> Parse this CSV data: name,age,city\nAlice,30,NYC\nBob,25,LA
> Show this tab-separated data as a table: [paste TSV]
> Display this CSV nicely
```

---

### `regex_search`

Search text using a regular expression and return all matches.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | yes | Regular expression pattern |
| `text` | string | yes | Text to search in |

**Returns:** List of all matches found.

**Example prompts:**
```
> Find all email addresses in this text: [paste text]
> Extract all phone numbers from this document
> Find all URLs in this HTML snippet
> Get all numbers from: "Order #1234 costs $56.78 and ships in 3 days"
```

---

### `regex_replace`

Replace all matches of a regex pattern in text.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | yes | Regular expression pattern |
| `replacement` | string | yes | Replacement string |
| `text` | string | yes | Text to modify |

**Returns:** Modified text with all matches replaced.

**Example prompts:**
```
> Replace all whitespace with underscores in: "Hello World Example"
> Remove all HTML tags from this text: [paste HTML]
> Redact all email addresses in this document (replace with [EMAIL])
> Convert camelCase to snake_case in this variable list
```

---

## Usage Examples

### Parsing an API Response

```
> I got this API response. What is the user's name?
> {"status": "ok", "data": {"user": {"name": "Alice", "id": 42}}}

  ↳ routing: generalist → tool_use
  ⚙ tool: jq_query
    → Alice
  ↳ routing: tool_use → generalist

The user's name is Alice.
```

### Extracting Data

```
> Find all email addresses in this log file excerpt:
> user alice@example.com logged in; error sent to admin@company.org

  ↳ routing: generalist → tool_use
  ⚙ tool: regex_search
    → ["alice@example.com", "admin@company.org"]
  ↳ routing: tool_use → generalist

Found 2 email addresses: alice@example.com and admin@company.org.
```

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [Math Tools](math.md) — Numeric calculations
- [File Tools](files.md) — Read files for text processing
