# Host setup

You are here because the state probe identified that the assistant is on the participant's host machine, before a Linux environment with Claude Code is in place. This file covers the path from that state to a running Claude Code session inside a Linux environment, with the participant package on disk and the skill loaded. Once that is in place, [in-vm-setup.md](in-vm-setup.md) takes over.

Two paths split by the host's operating system. Identify the host with `uname -s` (or the host AI's equivalent runtime probe).

- `Linux`: native-Linux path. The host *is* the Linux environment. Skip the VM section and go straight to *Inside the Linux environment* below.
- `Darwin` (macOS): macOS path. Pick the VM tool that matches the host architecture (Apple Silicon: Multipass; Intel: Lima); UTM is the GUI-driven fallback.
- `MINGW*`, `MSYS*`, `CYGWIN*` (Windows-side bash variants): Windows path. Use WSL2 with Ubuntu 24.04. WSL2 is itself the Linux environment, so once it is installed and a shell opens inside it, the rest of this file follows the native-Linux path.

The Linux environment must satisfy at least 4 vCPUs, 8 GB of RAM, a 20 GB virtual disk, and Ubuntu 22.04 or 24.04 (or an equivalent distribution). The launch commands below provision these for VM users.

## Warning: Docker Desktop is not a substitute

The mock environment runs Docker Engine *inside* the Linux environment, not on the host. Docker Desktop on macOS or Windows does not satisfy this; the in-VM phase installs Docker Engine itself.

## macOS, Apple Silicon: Multipass

Homebrew (https://brew.sh) must be present. Then:

```
brew install --cask multipass
multipass launch lts --name task --cpus 4 --memory 8G --disk 20G
multipass shell task
```

`multipass shell task` opens an interactive shell inside the VM. From that shell, follow *Inside the Linux environment* below.

## macOS, Intel: Lima

Homebrew must be present. Then:

```
brew install lima
limactl start --name=task --cpus=4 --memory=8 --disk=20 \
    --tty=false template:ubuntu-24.04
limactl shell task
```

`limactl shell task` opens an interactive shell inside the VM.

## macOS fallback: UTM

If neither Multipass nor Lima works on the host, UTM (https://mac.getutm.app) is a secondary option: free, open source, GUI-driven. Install Ubuntu 24.04 from the official ISO. Setup takes longer than the CLI tools because the Ubuntu installer runs interactively. After install, log into the VM through UTM's console.

## Windows: WSL2

Install WSL2 with an Ubuntu 24.04 distribution following the official Microsoft instructions at https://learn.microsoft.com/en-us/windows/wsl/install. Once installed, open the Ubuntu shell from the Start menu, or run `wsl` from a Windows terminal. The shell drops you inside the WSL2 distribution, which is the Linux environment.

WSL2 shares the host filesystem under `/mnt/c/`, but the participant package, workspace, and mock environment live entirely on the WSL2 filesystem (`/home/<wsl-user>/...`); cross-filesystem operations are slow and pollute Windows-side metadata.

## Inside the Linux environment

You are now in a shell inside the Linux environment, regardless of which path got you here. The remaining steps put the participant package on this filesystem, install Claude Code, and hand off to the in-VM phase.

### 1. Get the participant package inside the Linux environment

Re-download the package from the public release URL. This is the simplest path on every host: no host-to-VM file transfer, no shared-folder configuration. The same URL the host AI fetched the package from earlier:

```
cd ~
curl -L -o participant-package.zip \
    https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/participant-package/participant-package.zip
unzip participant-package.zip
```

The unzipped tree sits at `~/participant-package/`. Inside, the skill is at `~/participant-package/.claude/skills/bsc-apm-study-helper/`.

If the participant prefers to transfer from the host instead (`multipass transfer` for Multipass, `limactl copy` for Lima, the WSL2 shared filesystem for WSL2, `scp` for UTM), that is also fine; the result is the same tree on the Linux filesystem.

### 2. Install Claude Code

Anthropic ships a shell installer. Download it first, read it (or have the participant read it), then run it; do not pipe directly to bash:

```
curl -fsSL https://claude.ai/install.sh -o /tmp/install-cc.sh
bash /tmp/install-cc.sh
claude --version
```

`claude --version` prints the installed version. If the command is not found, the installer's PATH update has not taken effect yet; either open a new shell or `source` the rc file the installer printed.

If the URL above fails to resolve at the time of install, fall back to the official Claude Code install instructions at https://docs.claude.com/en/docs/claude-code.

### 3. Log in

The participant has credentials for the Anthropic Claude Max subscription, given to them privately. The login flow is theirs alone; the assistant does not see, ask for, store, or echo the credentials. Tell the participant to run `claude` and follow the in-product login flow:

```
claude
```

The first run prompts for sign-in. The participant follows the prompts using the credentials they were provided. When login completes, the participant tells the assistant; the assistant takes that at face value and moves on.

### 4. Open Claude Code in the participant-package directory

The skill is project-scoped: Claude Code discovers it natively only when opened with the participant-package directory as its working directory. From the Linux shell:

```
cd ~/participant-package
claude
```

The skill loads inside this Claude Code session. From here, Claude Code itself drives the rest of the work: re-run the state probe, dispatch to [in-vm-setup.md](in-vm-setup.md), and continue.

## What you do not do here

- Do not install the case-study toolchain (Docker, gcc, valgrind, uv, gh, etc.) yet. That belongs to [in-vm-setup.md](in-vm-setup.md), and runs from inside the Linux environment under Claude Code's drive.
- Do not clone the codebases yet. They live in the workspace, not in the participant-package directory; [in-vm-setup.md](in-vm-setup.md) creates the workspace and clones them.
- Do not start a session yet. Sessions begin in [session.md](session.md), and only after in-VM setup is complete.
