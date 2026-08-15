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

## Viewing the Documentation

This documentation is pre-built and included in the binary distribution as HTML. Simply open `docs/index.html` in your web browser after extracting the binary package.

For development/editing, see the main repository documentation.

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

## Notes for Users

This documentation is included in your OpenJarvis distribution. It provides:

- **Installation:** Already done! You have the binary.
- **Configuration:** Setting up `specialists.yaml`
- **Usage:** Command-line options and features
- **Troubleshooting:** Common issues and solutions
- **Tools Reference:** All 29 built-in tools
- **FAQ:** Answers to common questions

Everything you need is self-contained in this documentation.
