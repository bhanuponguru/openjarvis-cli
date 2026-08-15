# Web Tools

OpenJarvis includes 3 web tools for searching the internet and fetching content.

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

## How Tools Are Invoked

You don't call tools directly — specialists invoke them automatically. Just ask naturally:

```
> What's the current price of Bitcoin?

  ↳ routing: generalist → knowledge → tool_use
  ⚙ tool: search_web
    → [{"title": "Bitcoin Price...", "url": "...", "snippet": "..."}]
  ↳ routing: tool_use → knowledge → generalist

The current price of Bitcoin is approximately $65,000 USD...
```

---

## Tool Access Requirements

Web tools require a specialist to have `tool_use` in its `delegates_to`:

```yaml
specialists:
  knowledge:
    system_prompt: "Knowledge specialist. End with [RETURN]."
    base_url: "..."
    model: "..."
    delegates_to: ["tool_use"]   # Required for web tool access

  tool_use:
    system_prompt: "Tool specialist. End with [RETURN]."
    base_url: "..."
    model: "..."
```

---

## Rate Limits

`search_web` uses DuckDuckGo's search API, which has informal rate limits. If you make many searches in rapid succession, you may see empty results or errors. This resolves automatically after a short pause.

---

## Privacy

- `search_web` sends queries to DuckDuckGo (privacy-focused, no personal tracking)
- `fetch_url` sends requests directly to the target website
- No search data is stored by OpenJarvis

For fully private operation, use Ollama with offline tools only and avoid web tools.

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [Configuration](../configuration/overview.md) — Set up tool access
- [Troubleshooting](../troubleshooting.md) — Web tool issues
