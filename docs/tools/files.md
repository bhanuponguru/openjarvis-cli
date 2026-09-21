# File Tools

OpenJarvis includes 9 file system tools for reading, writing, searching, and managing files and directory trees.

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

### `search_dir`

Recursively search for a string or regex pattern across files in a directory tree.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search_term` | string | required | Literal string or regex pattern to match |
| `dir_path` | string | `"."` | Root directory to search within |

**Returns:** List of matching dicts with `file`, `line`, and `content` (up to 100 matches).

---

### `search_file`

Search for a string or regex pattern in a specific file.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search_term` | string | required | Literal string or regex pattern to match |
| `file_path` | string | required | Path to the target file |

**Returns:** List of matching dicts with `line` and `content`.

---

### `find_file`

Find files matching a filename or glob pattern in a directory tree.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_name` | string | required | Filename or glob pattern (e.g. `"*.py"`) |
| `dir_path` | string | `"."` | Root directory to search within |

**Returns:** Sorted list of relative file paths matching the pattern.

---

## Usage Examples

### Reading a Configuration File

```text
oj> Read my .openjarvis/config.yaml and explain what it does

  ⚙ tool: read_file {"path": ".openjarvis/config.yaml"}
    → "root_agent:\n  name: root\n..."

Your `.openjarvis/config.yaml` defines the Root Agent coordinator and specialized agent profiles...
```

### Writing a Project Summary

```text
oj> List the files here and write a quick summary to summary.md

  [agent-coder] ⚙ list_directory {"path": "."}
    → ["src", "tests", "README.md", "pyproject.toml"]
  [agent-coder] ⚙ write_file {"path": "summary.md", "content": "# Project Summary\n..."}
    → "Successfully wrote to summary.md"

I have inspected the project directory and generated `summary.md`.
```

---

## Security Considerations

File tools operate with the permissions of the active user:
- **`read_file`**: Safely read code and configuration files.
- **`write_file`**: Writes or appends text to local files.
- **`delete_file`**: Deletion is permanent. Use with care.

---

## See Also

- [Tools Overview](overview.md) — All 49 built-in tools
- [Code Execution](code.md) — Subprocess execution
- [Data Processing](data.md) — Parsing CSV, JSON, and regex searches
