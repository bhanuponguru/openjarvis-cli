# Memory Tools

OpenJarvis includes 4 memory tools for storing and retrieving notes within a session.

---

## Tools

### `store_note`

Save a note under a key name.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | yes | Note name/identifier |
| `content` | string | yes | Content to store |

**Returns:** Confirmation message.

**Example prompts:**
```
> Remember that my project deadline is September 30
> Save a note called "api_key_reminder": The API key is in the .env file
> Store my preferences: I prefer concise responses with code examples
```

---

### `recall_note`

Retrieve a previously stored note.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | yes | Note name to retrieve |

**Returns:** Note content, or an error if the key doesn't exist.

**Example prompts:**
```
> What was my project deadline?
> Recall the note "api_key_reminder"
> What preferences did I save earlier?
```

---

### `list_notes`

List all stored note keys.

**Parameters:** None

**Returns:** List of all note keys, or empty list if none exist.

**Example prompts:**
```
> What notes have I saved?
> List all my stored notes
> Show me everything I've asked you to remember
```

---

### `delete_note`

Delete a stored note.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `key` | string | yes | Note key to delete |

**Returns:** Confirmation message, or an error if the key doesn't exist.

**Example prompts:**
```
> Delete the note "old_reminder"
> Remove the note called "temp"
> Clear my "deadline" note
```

---

## Usage Examples

### Saving Context During a Session

```
> Remember that we're working on the user authentication module

  ↳ routing: generalist → tool_use
  ⚙ tool: store_note
    → Stored note: context
  ↳ routing: tool_use → generalist

Got it! I've saved that we're working on the user authentication module.
```

Later in the same session:

```
> What were we working on again?

  ↳ routing: generalist → tool_use
  ⚙ tool: recall_note
    → we're working on the user authentication module
  ↳ routing: tool_use → generalist

We were working on the user authentication module.
```

### Tracking Multiple Items

```
> Save these three things: bugs found: login timeout, session not clearing, 
> password reset email not sending

  ↳ routing: generalist → tool_use
  ⚙ tool: store_note
    → Stored note: bugs
  ↳ routing: tool_use → generalist

I've saved all three bugs to a note called "bugs".

> What bugs did we find?

  ⚙ tool: recall_note
    → login timeout, session not clearing, password reset email not sending
```

---

## Session Scope

Notes are stored **in memory only** for the current session. They are lost when you exit OpenJarvis (`exit`, `quit`, or Ctrl+C).

For persistent storage across sessions, use the `write_file` tool to save notes to disk:

```
> Save my project notes to notes.md

  ⚙ tool: recall_note  (retrieves the note)
  ⚙ tool: write_file   (saves to disk)
```

---

## See Also

- [Tools Overview](overview.md) — All 29 tools
- [File Tools](files.md) — Persistent file-based storage
