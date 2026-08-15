# OpenJarvis User Documentation

This directory contains the standalone user documentation for the OpenJarvis client. This documentation is **completely separate** from the main repository documentation and is designed to be distributed independently with binary releases.

---

## Documentation Structure

```
docs/
├── mkdocs.yml                     # MkDocs configuration
├── index.md                       # Landing page
├── getting-started/
│   ├── installation.md            # Installation guide
│   ├── quick-start.md             # Quick start guide
│   └── first-steps.md             # First steps tutorial
├── configuration/
│   ├── overview.md                # Configuration overview
│   ├── specialists.md             # Specialist configuration
│   ├── providers.md               # Provider-specific guides
│   └── advanced.md                # Advanced configuration
├── tools/
│   ├── overview.md                # Tools overview
│   ├── web.md                     # Web tools
│   ├── math.md                    # Math tools
│   ├── files.md                   # File tools
│   ├── code.md                    # Code execution tools
│   ├── datetime.md                # Date/time tools
│   ├── text.md                    # Text processing tools
│   ├── system.md                  # System tools
│   └── memory.md                  # Memory tools
├── usage/
│   ├── cli.md                     # Command-line usage
│   ├── python-api.md              # Python API
│   └── routing.md                 # Routing protocol
├── troubleshooting.md             # Troubleshooting guide
└── faq.md                         # FAQ
```

---

## Building the Documentation

### Install Dependencies

```bash
# From project root
uv sync --group docs
```

### Local Development Server

```bash
cd packages/openjarvis/docs
uv run mkdocs serve
```

Open http://localhost:8000 to view the documentation.

### Build Static Site

```bash
cd packages/openjarvis/docs
uv run mkdocs build --strict
```

The built HTML will be in `site/`.

---

## Documentation vs Main Repo Docs

| This Documentation (`packages/openjarvis/docs/`) | Main Repo Docs (`docs/`) |
|--------------------------------------------------|--------------------------|
| **User-facing** — End users of OpenJarvis | **Developer-facing** — Contributors and maintainers |
| **Distributable** — Shipped with binaries | **Private** — Internal development docs |
| **Product docs** — OpenJarvis client only | **Technical docs** — Entire project (client + server) |
| **Standalone** — Complete, self-contained | **Comprehensive** — Architecture, internals, training |

---

## Key Principles

### Audience

This documentation is for **end users** who:
- Want to install and use OpenJarvis
- Need configuration help
- Want to understand features and capabilities
- Need troubleshooting assistance

This documentation is **NOT** for:
- Developers contributing to OpenJarvis (use main repo docs)
- jarvis server internals (separate documentation)
- Training details, architecture internals, or implementation details

### Content Guidelines

- **User-centric:** Focus on what users want to accomplish
- **Complete:** Self-contained, no dependency on main repo docs
- **Practical:** Examples, commands, configurations
- **Accessible:** Clear language, no jargon without explanation
- **Up-to-date:** Keep in sync with code changes

### No Cross-References

Do not link to:
- Main repository `docs/` folder
- Developer guides
- Architecture documents
- Training documentation

These docs must stand alone.

---

## Deployment

### Binary Releases

The release workflow builds this documentation and includes it in binary distributions:

```
openjarvis-X.X.X-linux-x86_64/
├── openjarvis                    # Binary
├── specialists.example.yaml      # Example config
├── README.md                     # Quick reference
└── docs/                         # This documentation (built HTML)
    ├── index.html
    ├── getting-started/
    ├── configuration/
    └── ...
```

Users can open `docs/index.html` in their browser to view the full documentation offline.

### Online (Future)

When deployed online, this documentation will be at a user-facing URL like:
- `https://openjarvis.dev` or
- `https://docs.openjarvis.dev`

---

## Maintenance

### When to Update

Update this documentation when:
- Adding/removing features
- Changing configuration format
- Adding/removing tools
- Fixing bugs that affect user experience
- Improving installation process

### What to Update

- **Configuration examples:** Keep in sync with `specialists.yaml` format
- **Command-line options:** Match `cli.py` implementation
- **Tool list:** Match tools in `builtin_tools/`
- **Error messages:** Reflect actual error text from code
- **Troubleshooting:** Add solutions for common issues

### Testing

Before committing documentation changes:

1. **Build test:** `mkdocs build --strict` must succeed
2. **Link test:** Check all internal links work
3. **Example test:** Verify configuration examples are valid YAML
4. **Command test:** Verify command-line examples work

---

## Style Guide

### Headings

- Use `#` for page title
- Use `##` for main sections
- Use `###` for subsections
- Use `---` horizontal rules between major sections

### Code Blocks

Always specify language:

````markdown
```bash
openjarvis --help
```

```yaml
generalist:
  model: "gpt-4o-mini"
```

```python
from openjarvis import Conductor
```
````

### Examples

Show both command and expected output:

````markdown
```bash
$ openjarvis --version
OpenJarvis version 0.1.0
```
````

### Admonitions

Use for important notes:

```markdown
!!! warning "Security Warning"
    Code execution runs on your machine. Only execute trusted code.

!!! info "Tip"
    Use Ollama for completely local, private AI assistance.

!!! note "Note"
    This feature requires version 0.2.0 or later.
```

### File Paths

Use inline code for file paths:
- `specialists.yaml`
- `/usr/local/bin/openjarvis`
- `~/.config/openjarvis/specialists.yaml`

### UI Elements

Use inline code for UI elements:
- Click "Run anyway"
- Type `exit` or `quit`
- Press **Ctrl+C**

---

## Questions?

For questions about this documentation structure, see:
- Main repository [DEVELOPER_GUIDE.md](../../../docs/DEVELOPER_GUIDE.md)
- Project [AGENTS.md](../../../AGENTS.md)

For questions about content, create an issue on GitHub.
