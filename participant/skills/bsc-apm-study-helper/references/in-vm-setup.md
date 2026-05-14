# In-VM setup

You are here because the Linux environment is up, Claude Code is installed inside the VM, and the participant has completed authentication. The remaining setup steps prepare the environment for the sessions: install the toolchain, install and start the mock environment, create the workspace and clone the two codebases, wire MCP. After this file, [session.md](session.md) covers per-session framework CLI install and the session lifecycle.

These steps run the same commands wherever you are running. From the host, wrap each command in the VM tool's shell wrapper (`limactl shell task -- bash -c '<command>'` for Lima, `wsl -d task -- bash -c '<command>'` for WSL2). From inside the VM, run them directly.

Order: toolchain, then mock environment, then workspace and codebases.

## Toolchain

The case-study work needs a container runtime (Docker Engine with Compose v2), a C build chain (`gcc`, `make`, `valgrind`, `pkg-config`, plus the `libcurl` and `libxml2` development headers), two scripting runtimes (Python 3.10 or newer with `uv`, and Node.js with `npm`), and a handful of command-line utilities (`git`, `curl`, `tar`, `zip`, `unzip`, `openssl`, `bash` 3.2 or newer, `gh`). The wrap-up step at the end of each session uses `zip` to package the submission, so it must be present before session 1 ends.

Install Docker first via the official convenience script. Download it before running so you can inspect it:

```
curl -fsSL https://get.docker.com -o /tmp/install-docker.sh
sudo sh /tmp/install-docker.sh
sudo usermod -aG docker $USER
```

The new `docker` group membership takes effect on the next login or after `newgrp docker`. Within Claude Code, prefer `sg docker -c '<cmd>'` instead of `newgrp`: `sg` runs the command in a subshell with the docker group active for that single invocation and returns control to the parent shell, so the conversation's working shell is preserved.

Install everything else with apt and the official uv installer:

```
sudo apt-get update
sudo apt-get install -y \
    build-essential pkg-config valgrind \
    libcurl4-openssl-dev libxml2-dev \
    git curl tar zip unzip openssl gh python3 python3-pip npm
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/install-uv.sh
sh /tmp/install-uv.sh
```

If `uv --version` reports `command not found` immediately after the install, run `source ~/.local/bin/env` once or open a new login shell so the installer's PATH update takes effect. The C minimums are `gcc` 9.0 (for C11), `libcurl` 7.81.0, `libxml2` 2.9.13; Ubuntu 22.04 and 24.04 both satisfy them. Verify the toolchain:

```
gcc --version
pkg-config --modversion libcurl
pkg-config --modversion libxml-2.0
valgrind --version
python3 --version
node --version
npm --version
uv --version
```

## Mock environment

The mock environment is a self-contained, containerised stack the participant runs locally during each session. It exposes the surfaces the implementation needs to integrate with, pre-loaded with test data so every participant runs against identical state.

### Download and install

Two architecture-specific releases ship from the same repository as the participant package:

- Tag `bsc-apm-case-study-task` ships `bsc-apm-amd64.tar.gz` for x86_64 hosts (Intel and AMD Linux machines, the Linux VM on an Intel Mac).
- Tag `bsc-apm-case-study-task-arm64` ships `bsc-apm-arm64.tar.gz` for arm64 hosts (Apple Silicon Macs running a Linux VM, arm64 Linux servers).

Identify architecture with `uname -m`: `x86_64` means amd64, `aarch64` or `arm64` means arm64. Pick a prefix on disk for the mock environment, separate from the workspace (`<mock>` is the placeholder; `~/.bsc-apm` is a reasonable default). Run *one* of the two download commands below, the one that matches the architecture:

```
mkdir -p <mock> && cd <mock>

# x86_64 hosts:
curl -L -o bsc-apm-amd64.tar.gz \
    https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/bsc-apm-case-study-task/bsc-apm-amd64.tar.gz

# arm64 hosts:
curl -L -o bsc-apm-arm64.tar.gz \
    https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/bsc-apm-case-study-task-arm64/bsc-apm-arm64.tar.gz
```

Then unpack and bring the stack up. `./install` loads the bundled Docker images, generates self-signed TLS certificates into `./certs/`, and writes a pre-configured `.env` alongside. `./scripts/up` brings the three containers up, performs openeclass's first-time install on first run, and applies the test data; this takes a few minutes on a clean host:

```
tar -xzf bsc-apm-*.tar.gz
./install
./scripts/up
```

The stack listens on two URLs once it is ready:

- `http://localhost/` for the openeclass instance.
- `https://localhost:18443/` for the mock authentication service.

Ports 80 and 18443 must be free on the Linux environment. Port 80 is the default HTTP port and is more commonly held by another service than 18443 is; before running `./scripts/up`, check both with `ss -ltn '( sport = :80 or sport = :18443 )'`. If either is held, identify the holder (`sudo lsof -iTCP:<port> -sTCP:LISTEN` or `sudo fuser <port>/tcp`), state a concise plan for freeing it, and ask the participant for permission before stopping anything. Do not propose changing the port mapping; the testing environment depends on these specific ports.

### Lifecycle commands

Once installed, manage the environment from its prefix:

- `./scripts/up`: bring the stack up. Idempotent.
- `./scripts/down`: stop the stack; named volumes survive.
- `./scripts/status`: probe each service from the mock side and report whether the stack itself is healthy.
- `./scripts/verify-mcp --mcp-root <path>`: consumer-side complement to `status`; probes whether an `eclass-mcp-server` checkout authenticates against the mock with the `.env` and `certs/` it has been given, and prints `wiring ok` on success. Run only at initial setup or after a between-sessions reset, when the checkout is at the pinned baseline (`dbd2d16`) with no tracked-file changes; the script verifies wiring against the baseline auth code only and refuses to run otherwise.
- `./scripts/logs`: tail container logs.
- `./scripts/reset`: drop database state and re-apply the test data.

A reset during a session is unusual and reserved for unusual situations (for instance, recovering after a destructive experiment by the AI); when needed, `./scripts/reset` returns the environment to its initial state.

### Uninstall

To remove the mock environment from the machine after the study, stop the stack and drop its volumes (`down -v`), remove the loaded images, and delete the prefix:

```
docker compose -f <mock>/compose.yaml down -v
docker rmi bsc-apm/openeclass:dev bsc-apm/mock-cas:dev
rm -rf <mock>
```

## Workspace and codebases

The participant package's `task/` directory holds `PRD.md` (the requirements the participant implements against) and `PROMPT.md` (the message the participant gives the AI to open the session). The *workspace* is the directory in which the participant opens Claude Code on the Linux environment for sessions; it is the AI's working directory for the session, separate from the participant-package directory.

The workspace must end up with this exact layout:

```
<workspace>/
|-- PRD.md
|-- PROMPT.md
|-- eclass-mcp-server/      # implementation codebase
`-- openeclass/             # legacy PHP codebase, read-only reference
```

Create the workspace as a fresh directory of the participant's choice (`~/workspace/` is your default; before creating it, announce the default in plain terms and offer the participant the chance to specify a different path).

```
mkdir -p <workspace>
```

Drop `PRD.md` and `PROMPT.md` into the workspace. How you get them in depends on where the participant package currently lives:

- If the participant package is on the same filesystem as the workspace (native Linux, or you're running inside the VM with the package already there): copy them directly.

```
cp <participant-package>/task/PRD.md <workspace>/PRD.md
cp <participant-package>/task/PROMPT.md <workspace>/PROMPT.md
```

- If you are driving the VM from the host and the participant package is only on the host filesystem: stream the two files out of a fresh download of the package zip inside the VM, without unpacking the rest. `unzip -p` writes the named file to stdout; redirect each into the workspace.

```
cd <workspace>
curl -L -o /tmp/pkg.zip \
    https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/participant-package/participant-package.zip
command -v unzip >/dev/null || { sudo apt-get update && sudo apt-get install -y unzip ; }
unzip -p /tmp/pkg.zip participant-package/task/PRD.md > PRD.md
unzip -p /tmp/pkg.zip participant-package/task/PROMPT.md > PROMPT.md
rm /tmp/pkg.zip
```

Either way, the workspace ends up with both files at the root.

Clone `eclass-mcp-server` and check out the pinned commit `dbd2d16`. This commit is the patch baseline: every diff submitted is computed against it.

```
cd <workspace>
git clone https://github.com/sdi2200262/eclass-mcp-server.git
cd eclass-mcp-server
git checkout dbd2d16
uv sync --dev --all-extras
cd ..
```

Clone `openeclass` at its pinned commit `e8b3329`. The AI treats this codebase as a read-only reference, and the participant keeps it that way:

```
cd <workspace>
git clone https://github.com/gunet/openeclass.git
cd openeclass
git checkout e8b3329
cd ..
```

### MCP server configuration

The `.env` and `certs/` that `./install` wrote inside `<mock>` are everything the implementation needs to authenticate against the mock. Copy both into the `eclass-mcp-server/` checkout, preserving the `certs/` subdirectory:

```
cp <mock>/.env <workspace>/eclass-mcp-server/.env
cp -r <mock>/certs <workspace>/eclass-mcp-server/certs
```

The `.env` references the certificate by relative path, so no further configuration is required.

### Verify

Verify wiring with the testing environment's `verify-mcp` script, which performs a single SSO login and logout using the credentials in the just-copied `.env`:

```
<mock>/scripts/verify-mcp --mcp-root <workspace>/eclass-mcp-server
```

It prints `wiring ok` on success and names the missing file or environment variable on failure.

At this point in-VM setup is complete. The workspace is ready for the first session; framework CLI install and session start are covered in [session.md](session.md).
