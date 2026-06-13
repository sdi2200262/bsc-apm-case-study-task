# BSc APM Case Study - Task

This repository ships the BSc thesis case-study task: the task specification (PRD, PROMPT), the participant guide, helper scripts and a Claude Code helper skill, and the containerised testing environment the task runs against.

The thesis evaluates [Agentic Project Management (APM)](https://github.com/sdi2200262/agentic-project-management) against [GitHub Spec-kit](https://github.github.io/spec-kit/) for AI-assisted software development; the task and testing environment in this repository are framework-agnostic.

## Releases

Two release surfaces ship from this repository:

- **Participant package** (`participant-package` tag): `participant-package.zip` containing the task spec, guide PDF, helper scripts, and the Claude Code helper skill. Participants download and unpack this on their Linux environment.
- **Testing environment** (`bsc-apm-case-study-task` and `bsc-apm-case-study-task-arm64` tags): architecture-specific tarballs (`bsc-apm-amd64.tar.gz`, `bsc-apm-arm64.tar.gz`) carrying the containerised openeclass instance, mock authentication service, deterministic seed data, and lifecycle scripts. Participants install and run this locally during their case-study session; the grading machine installs and runs the same release when evaluating submissions.

The mock authentication service replicates the surface the [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reference client expects (Apereo CAS / SAML 1.1 against the University of Athens deployment), and identifies itself as a mock to inspecting agents through page copy, the `Server: bsc-apm-mock-cas` response header, and inline XML comments.

## Prerequisites

A Linux host (native, WSL2 with Docker Engine inside the distro, or a Linux VM on macOS) with Docker Engine and Compose v2, roughly 4 GB free RAM and 20 GB free disk, and Bash 3.2 or newer. TCP ports 80 (openeclass) and 18443 (mock authentication service) must be free before `./install`.

These are the testbed's own floor. Participants run it inside a Linux environment whose own floor is higher (4 vCPUs, 8 GB RAM, 20 GB disk); the participant guide states that floor.

## Install and run

```bash
# 1. Download the tarball for your architecture and extract it into <prefix>
ARCH=$(uname -m)
curl -L https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/<release-tag>/bsc-apm-${ARCH}.tar.gz \
    | tar -xz -C <prefix>

# 2. Install from inside <prefix> (loads the bundled images, generates the
#    self-signed SSL certs; idempotent)
cd <prefix>
./install

# 3. Bring the stack up (waits for healthchecks, applies the seed, prints
#    the localhost URLs the MCP server should target)
./scripts/up
```

`<prefix>` is where the environment lives (recommended `~/.bsc-apm/`); the participant chooses it, with no silent default.

## Lifecycle

Manage the running environment with the scripts under `scripts/`:

| Script | Purpose |
|---|---|
| `./scripts/up` | Bring the stack up; idempotent. |
| `./scripts/down` | Bring the stack down; named volumes survive. |
| `./scripts/status` | Probe each service from the mock side and report whether the stack is healthy. |
| `./scripts/verify-mcp --mcp-root <path>` | Consumer-side complement to `status`; probe whether an `eclass-mcp-server` checkout authenticates against this mock with the `.env` and `certs/` it was given. Prints `wiring ok`, or names the missing file or variable. Refuses to run unless the checkout is at the pinned baseline (`dbd2d16`) with no tracked-file changes. |
| `./scripts/logs` | Tail container logs. |
| `./scripts/reset-db` | Drop the database volume and re-apply the seed. |
| `./scripts/reset-cas` | Clear the mock authentication service's in-memory state. |
| `./scripts/reset-cache` | Clear the openeclass PHP opcache and session storage. |
| `./scripts/reset` | Run all three resets plus a fresh volume re-init; used by the grading machine before each run. |

## Architecture

Three services run in one Docker Compose stack under the pinned project name `bsc-apm-env`, with deterministic container names (`bsc-apm-env-{db,eclass,sso}-1`) regardless of install path.

- **`db`**: MariaDB 10.11 (upstream multi-arch image) holding the openeclass database; the `db_data` volume persists it across `down`/`up`. `eclass` waits on its healthcheck.
- **`eclass`**: Open eClass from upstream gunet, pinned to `Release_4.3.3` and built into `bsc-apm/openeclass:dev` at release-prep time (upstream `master` does not produce a working build). Exposes host port 80; `config_data`/`courses_data`/`video_data` preserve runtime state. The image is exactly the upstream platform with no sidecars; on a fresh database `scripts/up` runs openeclass's first-time install before seeding, so participants never see the install wizard.
- **`sso`**: the mock authentication service, `bsc-apm/mock-cas:dev` built from `mock-cas/`. Implements the Apereo CAS / SAML 1.1 surface the reference client expects. Exposes host port 18443 with self-signed TLS (the container listens on 8082, remapped at the host); certs under `<prefix>/certs/` mount read-only.

The eclass container reaches the mock through the docker bridge gateway `172.17.0.1:18443`, matching the seeded `auth_settings` row. From the host, `http://localhost/` serves the openeclass UI and API and `https://172.17.0.1:18443/` serves the mock.

The reference [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) reads the environment variables below; the values hold when the MCP server runs on the host with the environment up. The grading machine sets them from the install path; participants set them in their MCP server's `.env`, and the participant guide carries the concrete values.

| Variable | Value |
|---|---|
| `ECLASS_URL` | `http://localhost` |
| `ECLASS_USERNAME` | matches `seed/seed.yaml`'s `user.username` |
| `ECLASS_PASSWORD` | matches `seed/seed.yaml`'s `user.cas_password` |
| `ECLASS_SSO_DOMAIN` | `172.17.0.1:18443` |
| `ECLASS_SSO_PROTOCOL` | `https` |
| `SSL_CERT_FILE` | `<prefix>/certs/sso_cert.pem` |
| `REQUESTS_CA_BUNDLE` | `<prefix>/certs/sso_cert.pem` |
| `CURL_CA_BUNDLE` | `<prefix>/certs/sso_cert.pem` |

## Related

- [bsc-apm-thesis](https://github.com/sdi2200262/bsc-apm-thesis): thesis LaTeX source.
- [bsc-apm-case-study-infra](https://github.com/sdi2200262/bsc-apm-case-study-infra): grader, parser, scoring, and evaluation pipeline.
- [bsc-apm-case-study-data](https://github.com/sdi2200262/bsc-apm-case-study-data): participant submissions (private).
- [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server): reference MCP client for the openeclass platform.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

---

*Part of the BSc APM Case Study evaluating the Agentic Project Management (APM) framework, Department of Informatics and Telecommunications, University of Athens.*
