# BSc APM Case Study - Task

Task materials and containerised testing environment for the BSc thesis case study comparing [Agentic Project Management (APM)](https://github.com/sdi2200262/agentic-project-management) with [GitHub Spec-kit](https://github.github.io/spec-kit/) for AI-assisted software development.

The repository contains the task specification, participant guide and helper skill, deterministic seed data, and a portable Open eClass environment with a mock authentication service. The task and testing environment are framework-independent.

## Releases

The repository publishes three releases:

- [`participant-package`](https://github.com/sdi2200262/bsc-apm-case-study-task/releases/tag/participant-package) provides `participant-package.zip`, which contains the task specification, guide, and helper skill.
- [`bsc-apm-case-study-task`](https://github.com/sdi2200262/bsc-apm-case-study-task/releases/tag/bsc-apm-case-study-task) provides the AMD64 testing environment as `bsc-apm-amd64.tar.gz`.
- [`bsc-apm-case-study-task-arm64`](https://github.com/sdi2200262/bsc-apm-case-study-task/releases/tag/bsc-apm-case-study-task-arm64) provides the ARM64 testing environment as `bsc-apm-arm64.tar.gz`.

## Requirements

Run the testing environment on a Linux host, WSL2 distribution with Docker Engine, or Linux virtual machine. It requires Docker Engine with Compose v2, Bash 3.2 or newer, about 4 GB of free RAM, 20 GB of free disk space, and free TCP ports 80 and 18443.

## Install and run

The following commands select the release for the host architecture and install it under `~/.bsc-apm/`:

```bash
case "$(uname -m)" in
  x86_64) ARCH=amd64; RELEASE=bsc-apm-case-study-task ;;
  aarch64|arm64) ARCH=arm64; RELEASE=bsc-apm-case-study-task-arm64 ;;
  *) echo "unsupported architecture: $(uname -m)" >&2; exit 1 ;;
esac

PREFIX="$HOME/.bsc-apm"
mkdir -p "$PREFIX"
curl -fL "https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/$RELEASE/bsc-apm-$ARCH.tar.gz" \
  | tar -xz -C "$PREFIX"

cd "$PREFIX"
./install
./scripts/up
```

`./install` loads the bundled images and generates self-signed certificates. It is safe to run again. `./scripts/up` starts the services, waits for their health checks, applies the seed data, and prints the local service URLs.

## Environment commands

Run these commands from the installation directory:

| Command | Purpose |
|---|---|
| `./scripts/up` | Start the environment and apply the seed data. |
| `./scripts/down` | Stop the environment while preserving its volumes. |
| `./scripts/status` | Report service health. |
| `./scripts/logs` | Follow container logs. |
| `./scripts/reset` | Reset the database, authentication state, cache, and volumes. |
| `./scripts/reset-db` | Reset and reseed the database. |
| `./scripts/reset-cas` | Clear the mock authentication state. |
| `./scripts/reset-cache` | Clear Open eClass sessions and PHP opcode cache. |
| `./scripts/verify-mcp --mcp-root <path>` | Verify a clean reference MCP checkout and its environment configuration. |

## Architecture

Docker Compose runs three services under the project name `bsc-apm-env`:

- `db` runs MariaDB 10.11 and stores Open eClass data in a persistent volume.
- `eclass` runs Open eClass `Release_4.3.3` on `http://localhost/`.
- `sso` runs the mock CAS and SAML authentication service on host port 18443 with a self-signed certificate.

The seed source is [`seed/seed.yaml`](seed/seed.yaml). [`compose.yaml`](compose.yaml), [`install`](install), and the scripts under [`scripts/`](scripts/) define the runtime and lifecycle. The participant package source lives under [`participant/`](participant/).

## Related

- [bsc-apm-thesis](https://github.com/sdi2200262/bsc-apm-thesis): thesis LaTeX source.
- [bsc-apm-case-study-infra](https://github.com/sdi2200262/bsc-apm-case-study-infra): grader, parser, scoring, and evaluation pipeline.
- [bsc-apm-case-study-data](https://github.com/sdi2200262/bsc-apm-case-study-data): encrypted participant data.
- [eclass-mcp-server](https://github.com/sdi2200262/eclass-mcp-server): reference MCP client for Open eClass.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).

---

*Part of the BSc APM Case Study evaluating the Agentic Project Management (APM) framework, Department of Informatics and Telecommunications, University of Athens.*
