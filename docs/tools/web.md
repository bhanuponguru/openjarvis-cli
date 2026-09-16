# Web Tools

OpenJarvis includes 5 web tools for searching the internet, fetching content, executing HTTP REST requests, and inspecting OpenAPI specifications.

---

## Tools

### `search_web`

Search the web using DuckDuckGo and return the top results.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `num_results` | integer | 5 | Number of results to return (max ~10) |

**Returns:** List of results with title, URL, and snippet.

**Example prompts:**
```
> What are the latest developments in quantum computing?
> Search for Python async programming tutorials
> Find news about the Mars missions
```

---

### `fetch_url`

Fetch the text content of any webpage. HTML, scripts, and styles are stripped — you get clean readable text.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | URL to fetch |
| `timeout` | integer | 15 | Request timeout in seconds |

**Returns:** Plain text content of the page (truncated to ~8KB).

**Example prompts:**
```
> Fetch the content from https://example.com/article
> Get the text from this documentation page: https://docs.example.com
> What does this URL say: https://news.example.com/story
```

---

### `fetch_wikipedia`

Fetch a summary of a Wikipedia article on any topic.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `topic` | string | required | Topic to look up |
| `sentences` | integer | 5 | Number of sentences to return |

**Returns:** Summary text from Wikipedia.

**Example prompts:**
```
> Tell me about the history of Python programming language
> What is quantum entanglement?
> Explain the Roman Empire
```

---

### `http_request`

Execute an HTTP/REST API request with configurable methods, headers, query parameters, and JSON payloads.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Full destination URL (http/https) |
| `method` | string | `"GET"` | HTTP method (GET, POST, PUT, DELETE, PATCH, HEAD) |
| `headers` | object | `{}` | Optional request headers dict |
| `params` | object | `{}` | Optional query string parameters |
| `data` | string | `null` | Optional raw body string |
| `json_data` | object | `null` | Optional JSON body payload |
| `timeout` | integer | 15 | Timeout in seconds |

**Returns:** Dict with `status_code`, `headers`, and parsed `body` (JSON or truncated text).

---

### `parse_openapi_spec`

Parse and inspect an OpenAPI or Swagger 2.0/3.0 specification from raw text or local file.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `spec_text` | string | `null` | Raw JSON/YAML specification text |
| `spec_path` | string | `null` | File path to OpenAPI JSON/YAML file |

**Returns:** Dict with API title, version, endpoint count, and list of endpoints with methods, operations, and parameters.

---

## How Web Tools Are Invoked

You don't need to call tools manually — models invoke them automatically when answering prompts that require real-time knowledge or web content:

```text
oj> What's the latest price of Bitcoin?

  ↳ routing: generalist → knowledge
  ⚙ tool: search_web {"query": "Bitcoin price current USD"}
    → [{"title": "Bitcoin Price...", "url": "...", "snippet": "..."}]

The current price of Bitcoin is approximately $65,000 USD...
```

---

## Rate Limits & Privacy

- **DuckDuckGo Search (`search_web`)**: Queries DuckDuckGo without personal tracking or API keys.
- **Web Fetching (`fetch_url`)**: Requests the target URL directly, strips HTML scripts/styles, and truncates content to ~8KB.
- **Wikipedia (`fetch_wikipedia`)**: Fetches summary extracts for quick reference.

For air-gapped or 100% offline environments, avoid prompts that require live web access.

---

## See Also

- [Tools Overview](overview.md) — All 29 built-in tools
- [Configuration Guide](../configuration/overview.md) — Configuring specialists
- [Troubleshooting](../troubleshooting.md) — Common connection issues
