# OpenJarvis User Documentation

This directory contains the standalone user documentation for the OpenJarvis client. This documentation is **completely separate** from the main repository documentation and is designed to be distributed independently with binary releases.

---

## Documentation Structure

```
docs/
├── index.md                       # Landing page & architecture
├── getting-started/
│   ├── installation.md            # Installation & uv setup
│   ├── quick-start.md             # First CLI conversation
│   └── first-steps.md             # Key interactive concepts
├── configuration/
│   ├── overview.md                # Config YAML configuration
│   ├── agents.md                  # Agent profiles, personas & tool scoping
│   ├── providers.md               # LLM Provider setups (Ollama, OpenAI, Anthropic, etc.)
│   └── advanced.md                # Multi-specialist routing & air-gapped setup
├── tools/
│   ├── overview.md                # 49 Built-in tools overview
│   ├── editor.md                  # Code editor (str_replace) & bash execution
│   ├── git.md                     # Git diff, status, log, and patch tools
│   ├── web.md                     # Web browsing, DDGS search, HTTP REST, OpenAPI
│   ├── files.md                   # File I/O, search, & directory operations
│   ├── code.md                    # Sandboxed python execution, linting, pytest
│   ├── math.md                    # SymPy, stats, & math solvers
│   ├── datetime.md                # Timezone & date arithmetic
│   ├── data.md                    # JSON/CSV transforms, regex, SQLite
│   └── memory.md                  # Session and persistent memory operations
├── usage/
│   ├── cli.md                     # Command-line options & flags
│   └── routing.md                 # Multi-agent topology & consensus protocol
├── security.md                    # Permission levels & sandboxing
├── developer-guide.md             # Contributing, testing, & binary builds
├── troubleshooting.md             # Common errors & solutions
└── faq.md                         # Frequently asked questions
```

---

## Local Documentation Preview

To serve this documentation locally:

```bash
uv run --group docs mkdocs serve
```

To verify documentation builds with strict link checking:

```bash
uv run --group docs mkdocs build --strict
```

---

## Deployment

### Binary Releases

The release workflow builds this documentation and includes it in binary distributions:

```
openjarvis-X.X.X-linux-x86_64/
├── openjarvis                    # Binary
├── config.example.yaml           # Example config
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
- `https://openjarvis-cli.bhanuponguru.tech`

---

## Notes for Users

This documentation is included in your OpenJarvis distribution. It provides:

- **Installation:** Already done! You have the binary.
- **Configuration:** Setting up `.openjarvis/config.yaml`
- **Usage:** Command-line options and features
- **Troubleshooting:** Common issues and solutions
- **Tools Reference:** All 49 built-in tools across 9 domains
- **FAQ:** Answers to common questions

Everything you need is self-contained in this documentation.
