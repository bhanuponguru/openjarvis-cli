# Memory Tools

OpenJarvis includes persistent memory tools for creating, reading, updating, listing, and searching notes across sessions in both local (project) and global (user-wide) scopes.

---

## Storage Model

Memories are persisted as clean Markdown files inside:
- **Local scope** (project-specific): `./.openjarvis/memory/<name>.md`
- **Global scope** (user-wide): `~/.openjarvis/memory/<name>.md`

Agents can create, read, update, and search these memory files seamlessly without accessing raw disk paths.

---

## Tools

### `save_memory`

Create or overwrite a persistent memory file in markdown format.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | yes | — | Memory file name (without extension) |
| `content` | string | yes | — | Markdown text content to persist |
| `scope` | string | no | `"local"` | Storage scope: `"local"` or `"global"` |

**Example prompts:**
```
> Remember in my global notes that I prefer Python and concise answers
> Save a project memory called "architecture" with our DB schema decision
```

---

### `read_memory`

Read the contents of a persistent memory file.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | yes | — | Memory file name to read |
| `scope` | string | no | `"local"` | Storage scope: `"local"` or `"global"` |

**Example prompts:**
```
> What was our architecture decision for the database?
> Read the global memory "user_preferences"
```

---

### `update_memory`

Append or update information in an existing memory file.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | yes | — | Memory note name to update |
| `content` | string | yes | — | Content to append |
| `scope` | string | no | `"local"` | Storage scope: `"local"` or `"global"` |

---

### `list_memories`

List all available memory file names.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `scope` | string | no | `"local"` | Scope to list: `"local"`, `"global"`, or `"all"` |

---

### `search_memories`

Search across memory files for matching text queries.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | yes | — | Search keyword or term |
| `scope` | string | no | `"all"` | Scope to search: `"local"`, `"global"`, or `"all"` |

---

### Backward Compatibility

The legacy session note commands (`store_note`, `recall_note`, `list_notes`, `delete_note`) continue to work transparently by mapping to local persistent memory.

---

## See Also

- [Tools Overview](overview.md) — Summary of all built-in tools
- [Configuration Overview](../configuration/overview.md) — `.openjarvis` directory hierarchy
