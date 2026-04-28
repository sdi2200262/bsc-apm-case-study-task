# Install and Lifecycle

This document describes how to install and operate the participant testing environment locally.

## Prerequisites

- Linux host: native Linux, WSL2 with Docker Engine inside the distro, or macOS via a Linux VM (Multipass running Ubuntu 22.04+ recommended).
- Docker Engine plus Compose v2.
- Approximately 4 GB free RAM and 20 GB free disk for images and named volumes.
- Bash 3.2 or newer for the lifecycle scripts.

## Install

1. Download the release tarball matching your host architecture:

   ```bash
   ARCH=$(uname -m)
   curl -L https://github.com/sdi2200262/bsc-apm-case-study-env/releases/download/vX.Y.Z/bsc-mock-vX.Y.Z-${ARCH}.tar.gz \
       | tar -xz -C <prefix>
   ```

   `<prefix>` is the directory where the environment will live. Recommended: `~/.bsc-mock/`. The participant chooses; there is no silent default.

2. Run the install script from inside the extracted directory:

   ```bash
   cd <prefix>
   ./install
   ```

   `install` loads the docker images bundled in the release, generates self-signed SSL certificates for the mock authentication service, and prints a "ready" message. It is idempotent; re-running is safe.

3. Bring the stack up:

   ```bash
   ./scripts/up
   ```

   On first run, this brings up the three services, waits for healthchecks, applies the seed data, and prints the localhost URLs the participant's MCP server should target.

## Lifecycle commands

Once installed, manage the environment with the scripts under `scripts/`:

| Script | Purpose |
|---|---|
| `./scripts/up` | Bring the stack up; idempotent. |
| `./scripts/down` | Bring the stack down; named volumes survive. |
| `./scripts/status` | Probe each service and report whether the stack is healthy. |
| `./scripts/logs` | Tail container logs. |
| `./scripts/reset-db` | Drop the database volume and re-apply the seed. |
| `./scripts/reset-cas` | Clear the mock authentication service's in-memory state. |
| `./scripts/reset-cache` | Clear the openeclass PHP opcache and session storage. |
| `./scripts/reset` | Run all three resets plus a fresh volume re-init. Used by the grading machine at the start of each grading run. |

## Localhost surface

Participants point their MCP server at:

- `http://localhost/` for the openeclass instance.
- `https://172.17.0.1:8082/` for the mock authentication service.

The full set of environment variables consumed by the reference [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) is documented in [ARCHITECTURE.md](ARCHITECTURE.md).
