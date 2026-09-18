# Data Processing Tools

OpenJarvis includes 6 data processing tools for parsing JSON, querying structured payloads, formatting CSV tables, executing regex matches, and querying SQLite databases.

---

## Tools

### `parse_json`

Parse, validate, and pretty-print a JSON string.

**Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `json_str` | string | yes | JSON string to parse |

**Returns:** Indented, formatted JSON string, or validation error.

**Example prompts:**
```text
> Parse and format this JSON: {"name":"Alice","age":30,"active":true}
> Pretty-print this API response: [paste minified JSON]
> Validate this JSON payload
```

---

### `jq_query`

Query a JSON string using dot-notation paths.

**Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `json_str` | string | yes | JSON string to query |
| `path` | string | yes | Dot-notation path (e.g. `users.0.name`) |

**Returns:** Extracted value at the path, or error if not found.

**Path syntax:**

| Path | Accesses |
| :--- | :--- |
| `name` | `{"name": "Alice"}` → `"Alice"` |
| `user.email` | `{"user": {"email": "..."}}` |
| `items.0` | First element of `items` array |
| `items.2.price` | `price` of third item |

**Example prompts:**
```text
> Extract the email from this JSON: {"user": {"name": "Alice", "email": "alice@example.com"}}
> Get the first item's price from: {"items": [{"name": "Book", "price": 9.99}]}
```

---

### `parse_csv`

Parse a CSV string and display it as an aligned table.

**Parameters:**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `csv_str` | string | required | CSV string to parse |
| `delimiter` | string | `","` | Field delimiter (e.g. `,`, `\t`, `\|`) |

**Returns:** Formatted Markdown table preview.

**Example prompts:**
```text
> Parse this CSV data: name,age,city\nAlice,30,NYC\nBob,25,LA
> Show this tab-separated data as a table: [paste TSV]
```

---

### `regex_search`

Search text using regular expressions and return matching substrings.

**Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pattern` | string | yes | Regular expression pattern |
| `text` | string | yes | Text to search in |

**Returns:** List of all regex matches found.

**Example prompts:**
```text
> Find all email addresses in this text: [paste text]
> Extract all phone numbers from this document
> Find all URLs in this HTML snippet
```

---

### `regex_replace`

Replace all occurrences matching a regex pattern in text.

**Parameters:**

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `pattern` | string | yes | Regular expression pattern |
| `replacement` | string | yes | Replacement string |
| `text` | string | yes | Text to modify |

**Returns:** Modified text with replacements applied.

**Example prompts:**
```text
> Replace all whitespace with underscores in: "Hello World Example"
> Redact all email addresses in this document (replace with [EMAIL])
```

---

### `sql_query`

Execute SQL statements against a SQLite database file or in-memory database.

**Parameters:**

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `query` | string | required | SQL query or multi-statement script to execute |
| `db_path` | string | `":memory:"` | Path to SQLite database file, or `":memory:"` for transient DB |

**Returns:** Formatted Markdown table preview of rows returned, or confirmation of rows affected.

**Example prompts:**
```text
> Query the database at app.db: SELECT * FROM users LIMIT 10;
> Create a table and insert test data in :memory:
```

---

## Usage Examples

### Parsing JSON Payloads

```text
oj> Extract the user email from: {"status": "ok", "user": {"name": "Alice", "email": "alice@example.com"}}

  ↳ routing: generalist → code
  ⚙ tool: jq_query {"json_str": "{\"status\": \"ok\", ...}", "path": "user.email"}
    → "alice@example.com"

The user's email address is **alice@example.com**.
```

### Regex Search

```text
oj> Find all email addresses in: user alice@example.com logged in; error sent to admin@company.org

  ↳ routing: generalist → code
  ⚙ tool: regex_search {"pattern": "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+", "text": "..."}
    → ["alice@example.com", "admin@company.org"]

Found 2 email addresses: **alice@example.com** and **admin@company.org**.
```

---

## See Also

- [Tools Overview](overview.md) — All 49 built-in tools
- [File Tools](files.md) — Reading and writing files
- [Code Tools](code.md) — Running scripts and linting code
