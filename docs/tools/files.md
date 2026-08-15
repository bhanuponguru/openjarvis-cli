# File Tools

OpenJarvis includes 6 file system tools for reading, writing, and managing files.

---

## Tools

### `read_file`

Read the text content of a file.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | string | required | File path (relative or absolute) |
| `max_chars` | integer | 8000 | Maximum characters to return |

**Returns:** File contents as text. Truncated at `max_chars` if the file is larger.

**Example prompts:**
```
> Read the file config.yaml
> Show me the contents of README.md
> Read /etc/hosts
```

---

### `write_file`

Write or append text to a file. Creates the file if it doesn't exist.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | string | required | File path |
| `content` | string | required | Content to write |
| `append` | boolean | `false` | If true, append instead of overwrite |

**Returns:** Confirmation message.

**Example prompts:**
```
> Write "Hello World" to output.txt
> Create a file called notes.md with my meeting summary
> Append this log entry to app.log: [INFO] Server started
```

⚠️ **Warning:** `write_file` overwrites existing files by default. Ask to append if you want to preserve existing content.

---

### `list_directory`

List files and directories at a path, optionally filtered by pattern.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | string | `"."` | Directory path |
| `pattern` | string | `"*"` | Glob pattern filter |

**Returns:** List of matching paths.

**Example prompts:**
```
> List all files in the current directory
> Show me all Python files in src/
> List everything in ~/Documents matching *.pdf
```

---

### `search_in_files`

Search for a text pattern across multiple files.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | string | required | Directory to search in |
| `pattern` | string | required | Text pattern to search for |
| `glob` | string | `"**/*"` | File pattern (e.g. `"**/*.py"`) |

**Returns:** List of matches with file path and line number. Limited to 100 matches.

**Example prompts:**
```
> Find all occurrences of "TODO" in the src/ directory
> Search for "API_KEY" in all Python files
> Find where "database_url" is defined in my project
```

---

### `file_info`

Get metadata about a file or directory.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | File or directory path |

**Returns:** Size in bytes, modification time, and type (file/directory).

**Example prompts:**
```
> What is the size of large-file.bin?
> When was config.yaml last modified?
> Is output/ a file or directory?
```

---

### `delete_file`

Delete a file. Cannot delete directories.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | File path to delete |

**Returns:** Confirmation message or error if file not found.

**Example prompts:**
```
> Delete the file temp.log
> Remove output.txt
```

⚠️ **Warning:** Deletion is permanent. There is no undo.

---

## Usage Examples

### Reading a Config

```
> Read my specialists.yaml and explain what it does

  ↳ routing: generalist → knowledge → tool_use
  ⚙ tool: read_file
    → generalist:\n  system_prompt: "..."\n  base_url: ...
  ↳ routing: tool_use → knowledge → generalist

Your specialists.yaml defines a generalist using gpt-4o-mini and three specialists...
```

### Writing a Summary

```
> Summarize this project and save it to summary.md

  ↳ routing: generalist → knowledge → tool_use
  ⚙ tool: list_directory
    → [src/, tests/, README.md, ...]
  ⚙ tool: read_file
    → ...
  ⚙ tool: write_file
    → File written successfully
  ↳ routing: tool_use → knowledge → generalist

I've read the project files and saved a summary to summary.md.
```

---

## Security Considerations

File tools can read and write anywhere your user account has access, including sensitive system files.

**Best practices:**

- Run OpenJarvis from a project directory to limit scope
- Review file paths before allowing writes, especially for paths outside your working directory
- `delete_file` is irreversible — use with care
- `write_file` overwrites silently — always ask to append if preserving data matters

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [Code Execution](code.md) — Run scripts to process files
- [Troubleshooting](../troubleshooting.md) — Common file tool issues
