# Built-In Tools Overview

OpenJarvis includes 29 production-ready tools that specialists can invoke automatically.

---

## Tool Categories

| Category | Count | Tools |
|----------|-------|-------|
| **[Web](web.md)** | 4 | Search, fetch, HTTP GET/POST |
| **[Math](math.md)** | 3 | Calculate, solve equations, convert units |
| **[Files](files.md)** | 5 | Read, write, list, check existence, file info |
| **[Code Execution](code.md)** | 2 | Run Python, run shell commands |
| **[Date & Time](datetime.md)** | 5 | Current time/date, date calculations, formatting |
| **[Text Processing](text.md)** | 5 | Word count, JSON parsing, text manipulation |
| **[System](system.md)** | 2 | Environment variables, system information |
| **[Memory](memory.md)** | 3 | Save, retrieve, list notes |
| **Crypto** | 1 | Hash text (SHA-256) |

**Total:** 29 tools

---

## How Tools Work

### Automatic Invocation

Specialists invoke tools automatically — you don't need to explicitly request them.

**Example:**
```
> What's 15% of 200?

  routing: generalist → math → tool_use
  routing: tool_use → math → generalist

15% of 200 is 30.
```

The math specialist automatically delegated to tool_use, which invoked the `calculate` tool.

### Tool Delegation

Specialists can only use tools if they're configured to delegate to `tool_use`:

```yaml
math:
  delegates_to: ["tool_use"]  # Can use tools

creative:
  delegates_to: []  # Cannot use tools
```

### Tool Results

Tool results are returned to the calling specialist, which interprets them and returns a natural language response.

---

## Quick Reference

### Web Tools

```
> Search for the latest news about AI
> Fetch the content from https://example.com
> Make a GET request to https://api.example.com/data
> POST this data to https://api.example.com/endpoint
```

### Math Tools

```
> Calculate 15.5 * 234 + 67
> Solve for x: 2x + 5 = 15
> Convert 50 miles to kilometers
```

### File Tools

```
> Read the file config.yaml
> Write "Hello World" to output.txt
> List all files in the current directory
> Does the file data.json exist?
> Get information about the file large-file.bin
```

### Code Execution

```
> Run this Python code: print([x**2 for x in range(10)])
> Execute this shell command: ls -la
```

⚠️ **Security:** Code execution runs on your machine. Only execute trusted code.

### Date & Time Tools

```
> What's the current time?
> What's today's date?
> How many days between 2024-01-01 and 2024-12-31?
> Add 30 days to today's date
> Format 2024-08-15 as "August 15, 2024"
```

### Text Processing Tools

```
> Count the words in this text: [paste text]
> Extract JSON from this string: [paste string]
> Format this JSON nicely: {"a":1,"b":2}
> Truncate this text to 100 characters
> Replace all spaces with underscores in this text
```

### System Tools

```
> What's the value of the HOME environment variable?
> What's my system information?
```

### Memory Tools

```
> Save a note called "reminder": Call John at 3 PM
> Get the note "reminder"
> List all my saved notes
```

### Crypto Tools

```
> Hash this text using SHA-256: "Hello World"
```

---

## Tool Availability

All 29 tools are always available. Specialists automatically use tools when needed based on their task.

---

## Detailed Documentation

Click through to see detailed documentation for each category:

- **[Web Tools →](web.md)** — Search, fetch, HTTP requests
- **[Math Tools →](math.md)** — Calculations, equations, conversions
- **[File Tools →](files.md)** — File system operations
- **[Code Execution →](code.md)** — Run Python and shell commands
- **[Date & Time Tools →](datetime.md)** — Time and date operations
- **[Text Processing →](text.md)** — Text manipulation and JSON parsing
- **[System Tools →](system.md)** — Environment and system info
- **[Memory Tools →](memory.md)** — Persistent note storage

---

## Security Considerations

### Code Execution Tools

The `run_python` and `run_shell` tools execute arbitrary code on your machine. 

**Risks:**
- File system access
- Network access
- Process execution
- Data destruction

**Best Practices:**
- Only use with trusted inputs
- Review generated code before execution
- Run in isolated environments for untrusted code
- Consider disabling these tools in production

**Disabling code execution:** This feature is not yet implemented, but will be added in a future release.

### File System Tools

File tools can read and write anywhere your user has permissions.

**Best Practices:**
- Be careful with `write_file` — it can overwrite existing files
- Review file paths before allowing writes
- Consider running OpenJarvis with restricted permissions

### Web Tools

Web tools make outbound HTTP requests.

**Best Practices:**
- Be aware of rate limits on search APIs
- Don't send sensitive data to external APIs
- Review URLs before allowing requests

---

## Tool Error Handling

When a tool fails, specialists receive an error message and can retry or take alternative approaches.

**Example:**
```
> Read the file doesnt-exist.txt

  routing: generalist → knowledge → tool_use
  routing: tool_use → knowledge → generalist

I cannot read that file because it doesn't exist. Please verify the filename.
```

---

## Future Tools

Planned additions:

- Database tools (SQL queries)
- Email tools (send/receive)
- Calendar tools (schedule management)
- Image generation tools
- Audio/video processing tools
- Custom tool plugins

---

## See Also

- [Configuration](../configuration/overview.md) — Configure specialist tool access
- [Routing Protocol](../usage/routing.md) — How specialists invoke tools
- [Troubleshooting](../troubleshooting.md) — Common tool issues
