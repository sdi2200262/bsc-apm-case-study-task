# Install and Lifecycle

This document describes how to install and operate the participant testing environment locally.

## Prerequisites

- Linux host: native Linux, WSL2 with Docker Engine inside the distro, or macOS via a Linux VM (Multipass running Ubuntu 22.04+ recommended).
- Docker Engine plus Compose v2.
- Approximately 4 GB free RAM and 20 GB free disk for images and named volumes.
- Bash 3.2 or newer for the lifecycle scripts.
- TCP port 80 (openeclass) and TCP port 18443 (mock authentication service) free on the host. Free them before running `./install`.

## Install

1. Download the release tarball matching your host architecture:

   ```bash
   ARCH=$(uname -m)
   curl -L https://github.com/sdi2200262/bsc-apm-case-study-env/releases/download/<release-tag>/bsc-apm-${ARCH}.tar.gz \
       | tar -xz -C <prefix>
   ```

   `<prefix>` is the directory where the environment will live. Recommended: `~/.bsc-apm/`. The participant chooses; there is no silent default.

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
| `./scripts/status` | Probe each service from the mock side and report whether the stack itself is healthy. |
| `./scripts/verify-mcp --mcp-root <path>` | Consumer-side complement to `status`: probe whether an `eclass-mcp-server` checkout authenticates against this mock with the `.env` and `certs/` it has been given; prints `wiring ok` on success, names the missing file or environment variable on failure. Refuses to run if the checkout is not at the case-study's pinned baseline (`dbd2d16`) with no tracked-file changes, since the wiring is verified against the baseline auth code only. |
| `./scripts/logs` | Tail container logs. |
| `./scripts/reset-db` | Drop the database volume and re-apply the seed. |
| `./scripts/reset-cas` | Clear the mock authentication service's in-memory state. |
| `./scripts/reset-cache` | Clear the openeclass PHP opcache and session storage. |
| `./scripts/reset` | Run all three resets plus a fresh volume re-init. Used by the grading machine at the start of each grading run. |

## Localhost surface

Participants point their MCP server at:

- `http://localhost/` for the openeclass instance.
- `https://172.17.0.1:18443/` for the mock authentication service.

The full set of environment variables consumed by the reference [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server) is documented in [ARCHITECTURE.md](ARCHITECTURE.md).
