# BSc APM Case Study - Participant Testing Environment

Portable testing environment for the BSc APM Case Study evaluating the [Agentic Project Management (APM)](https://github.com/sdi2200262/agentic-project-management) framework against other approaches in AI-assisted software development.

## Overview

This repository ships a participant-facing testbed: a containerised openeclass instance, a mock authentication service, deterministic seed data, and lifecycle scripts. Participants install and run it locally during their case-study session; the grading machine installs and runs the same release when evaluating submissions.

The mock authentication service replicates the surface that the [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reference client expects (Apereo CAS / SAML 1.1 against the University of Athens deployment). The mock identifies itself as a mock to inspecting agents through page copy, response headers, and inline XML comments.

## Repository Structure

```
bsc-apm-case-study-env/
├── README.md
├── LICENSE
├── .gitignore
├── compose.yaml                # Three-service stack (db, eclass, sso)
├── install                     # Idempotent install entry script
├── Makefile                    # Release-prep targets
├── seed/                       # Editable seed data, generators, php seeder
│   ├── seed.yaml
│   ├── seed.json
│   ├── seed.php
│   ├── generate_seed_json.py
│   └── generate_cas_config.py
├── mock-cas/                   # Mock CAS authentication service
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   └── fixtures/
├── scripts/                    # Lifecycle commands
│   ├── up
│   ├── down
│   ├── status
│   ├── logs
│   ├── reset
│   ├── reset-db
│   ├── reset-cas
│   └── reset-cache
└── docs/
    ├── INSTALL.md
    └── ARCHITECTURE.md
```

## Documentation

- **[docs/INSTALL.md](docs/INSTALL.md)** - Install and lifecycle reference
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Stack overview, ports, and environment variables consumed by the participant's MCP server

## Related Repositories

- [bsc-apm-thesis](https://github.com/sdi2200262/bsc-apm-thesis) - Thesis LaTeX source
- [bsc-apm-case-study-task](https://github.com/sdi2200262/bsc-apm-case-study-task) - Task specification, grader, and participant guides
- [bsc-apm-case-study-data](https://github.com/sdi2200262/bsc-apm-case-study-data) - Participant submissions (private)
- [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) - Reference MCP client for the openeclass platform

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

---

*Part of BSc APM Case Study evaluating the Agentic Project Management (APM) framework - Department of Informatics and Telecommunications, University of Athens.*
