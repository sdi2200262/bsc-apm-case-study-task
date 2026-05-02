# BSc APM Case Study - Task

This repository ships the BSc thesis case-study task: the task specification (PRD, PROMPT), the participant guide, helper scripts and a Claude Code helper skill, and the containerised testing environment the task runs against.

The thesis evaluates [Agentic Project Management (APM)](https://github.com/sdi2200262/agentic-project-management) against [GitHub Spec-kit](https://github.github.io/spec-kit/) for AI-assisted software development; the task and testing environment in this repository are framework-agnostic.

## Releases

Two release surfaces ship from this repository:

- **Participant package** (`participant-package` tag) - `participant-package.zip` containing the task spec, guide PDF, helper scripts, and the Claude Code helper skill. Participants download and unpack this on their Linux environment.
- **Testing environment** (`bsc-apm-case-study-task` and `bsc-apm-case-study-task-arm64` tags) - architecture-specific tarballs (`bsc-apm-amd64.tar.gz`, `bsc-apm-arm64.tar.gz`) carrying the containerised openeclass instance, mock authentication service, deterministic seed data, and lifecycle scripts. Participants install and run this locally during their case-study session; the grading machine installs and runs the same release when evaluating submissions.

The mock authentication service replicates the surface that the [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reference client expects (Apereo CAS / SAML 1.1 against the University of Athens deployment). The mock identifies itself as a mock to inspecting agents through page copy, response headers, and inline XML comments.

## Repository Structure

```
bsc-apm-case-study-task/
├── README.md
├── LICENSE
├── .gitignore
├── Makefile                    # Release-prep targets (testing environment and participant package)
├── compose.yaml                # Three-service stack (db, eclass, sso)
├── install                     # Idempotent install entry script for the testing environment
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
├── scripts/                    # Lifecycle commands and consumer-side probe
│   ├── up
│   ├── down
│   ├── status
│   ├── logs
│   ├── reset
│   ├── reset-db
│   ├── reset-cas
│   ├── reset-cache
│   └── verify-mcp              # Auth-only wiring probe for an eclass-mcp-server checkout
├── participant/                # Participant package source
│   ├── guide/                  # Guide TeX source and built PDF
│   ├── task/                   # PRD, PROMPT, README
│   ├── scripts/                # Transcript helpers
│   └── skills/                 # Claude Code helper skill
└── docs/
    ├── INSTALL.md
    └── ARCHITECTURE.md
```

## Documentation

- **[docs/INSTALL.md](docs/INSTALL.md)** - Install and lifecycle reference for the testing environment
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Stack overview, ports, and environment variables consumed by the participant's MCP server

## Related Repositories

- [bsc-apm-thesis](https://github.com/sdi2200262/bsc-apm-thesis) - Thesis LaTeX source
- [bsc-apm-case-study-infra](https://github.com/sdi2200262/bsc-apm-case-study-infra) - Grader, parser, scoring, and evaluation pipeline
- [bsc-apm-case-study-data](https://github.com/sdi2200262/bsc-apm-case-study-data) - Participant submissions (private)
- [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) - Reference MCP client for the openeclass platform

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

---

*Part of the BSc APM Case Study evaluating the Agentic Project Management (APM) framework - Department of Informatics and Telecommunications, University of Athens.*
