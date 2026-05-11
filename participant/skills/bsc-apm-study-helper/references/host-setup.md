# Host setup

You are here because the participant needs a Linux environment for the study: to launch one if there isn't one yet, install Claude Code inside it, and complete the in-VM Claude Code login. Once those are done, you continue from wherever you are running. The rest of setup (toolchain, mock environment, workspace, clones) runs the same commands whether you drive them from the host via the VM tool's shell wrapper or from a Claude Code session opened inside the VM.

The participant package stays wherever you are running. When you're on a non-Linux host driving the VM through a shell wrapper, the package stays on the host filesystem; the VM only needs Claude Code installed and logged in, the toolchain, the mock environment, and a workspace directory with `PRD.md`, `PROMPT.md`, and the cloned codebases. The participant package itself does not enter the VM unless the participant decides to switch their helper to an in-VM Claude Code session (covered at the end of this file). On native Linux there is no boundary, and the participant package and the workspace both sit on the same filesystem.

The Claude Code login is the only step that must happen inside the VM, with the participant at the keyboard. That login binds the credentials the coordinator provided the participant to the VM, and the credentials are not to leave it.

Two paths split by the host's operating system. Identify the host with `uname -s`.

- `Linux`: the host *is* the Linux environment. Skip the VM section and go straight to *Setup inside the Linux environment* below; the package and the workspace both live on this one filesystem.
- `Darwin` (macOS): pick the VM tool that matches the host architecture (Apple Silicon: Multipass; Intel: Lima); UTM is the GUI-driven fallback.
- `MINGW*`, `MSYS*`, `CYGWIN*` (Windows-side bash variants): use WSL2 with Ubuntu 24.04. WSL2 is itself the Linux environment, so once it is installed and a shell opens inside it, the rest of this file follows the native-Linux path.

The Linux environment must satisfy at least 4 vCPUs, 8 GB of RAM, a 20 GB virtual disk, and Ubuntu 22.04 or 24.04 (or an equivalent distribution). The launch commands below provision these for VM users.

## Warning: Docker Desktop is not a substitute

The mock environment runs Docker Engine *inside* the Linux environment, not on the host. Docker Desktop on macOS or Windows does not satisfy this; the mock environment install in [in-vm-setup.md](in-vm-setup.md) installs Docker Engine itself.

## macOS, Apple Silicon: Multipass

Homebrew (https://brew.sh) must be present. Then:

```
brew install --cask multipass
multipass launch lts --name task --cpus 4 --memory 8G --disk 20G
multipass shell task
```

`multipass shell task` opens an interactive shell inside the VM.

## macOS, Intel: Lima

Homebrew must be present. Then:

```
brew install lima
limactl start --name=task --cpus=4 --memory=8 --disk=20 \
    --tty=false template:ubuntu-24.04
limactl shell task
```

`limactl shell task` opens an interactive shell inside the VM. Lima mounts the host's home directory into the VM and lands the new shell at the same path `limactl shell task` was launched from on the host (e.g. `/Users/<user>/Documents/...`), not at the VM's own home. Change to the VM's home before any interactive file operation, otherwise downloads and extractions land on the host mount:

```
cd ~
```

## macOS fallback: UTM

If neither Multipass nor Lima works on the host, UTM (https://mac.getutm.app) is a secondary option: free, open source, GUI-driven. Install Ubuntu 24.04 from the official ISO. Setup takes longer than the CLI tools because the Ubuntu installer runs interactively. After install, log into the VM through UTM's console.

## Windows: WSL2

Install WSL2 with an Ubuntu 24.04 distribution following the official Microsoft instructions at https://learn.microsoft.com/en-us/windows/wsl/install. Once installed, open the Ubuntu shell from the Start menu, or run `wsl` from a Windows terminal. The shell drops you inside the WSL2 distribution, which is the Linux environment.

WSL2 shares the host filesystem under `/mnt/c/`, but the workspace and mock environment live entirely on the WSL2 filesystem (`/home/<wsl-user>/...`); cross-filesystem operations are slow and pollute Windows-side metadata.

## Setup inside the Linux environment

The Linux environment is ready. Two remaining steps run inside the VM before the rest of setup: install Claude Code, then have the participant complete the login.

If you're on a non-Linux host, wrap each non-interactive command below in the VM tool's shell wrapper (`limactl shell task -- bash -c '<command>'` for Lima, `multipass exec task -- bash -c '<command>'` for Multipass, `wsl -- bash -c '<command>'` for WSL2). If you're inside the VM, run them directly. The Claude Code login is the exception: it must run interactively in a VM shell, with the participant at the keyboard.

### 1. Install Claude Code inside the VM

Anthropic ships a shell installer. Download it first, read it, then run it; do not pipe directly to bash:

```
curl -fsSL https://claude.ai/install.sh -o /tmp/install-cc.sh
bash /tmp/install-cc.sh
claude --version
```

`claude --version` prints the installed version. If the command is not found, the installer wrote its PATH update to a login-shell startup file (typically `~/.profile`) but the current shell is non-login (Lima's `limactl shell task` opens a non-login shell, for example), so the update has not been applied. The installer prints which file it wrote to; source that file, or open a new login shell, before continuing:

```
source ~/.profile     # or whichever file the installer named
claude --version
```

If the URL above fails to resolve at the time of install, fall back to the official Claude Code install instructions at https://docs.claude.com/en/docs/claude-code.

### 2. Log in (the only step that must happen inside the VM)

The participant has Claude Code credentials, provided privately by the coordinator. The login flow is theirs alone; you do not see, ask for, store, or echo the credentials. The participant opens an interactive VM shell themselves (`limactl shell task`, `multipass shell task`, the WSL2 shell from Start, or the UTM console) and runs:

```
claude
```

The first run prompts for sign-in. The participant follows the prompts with the credentials they were given. The directory the participant runs `claude` from does not matter at this point; the only goal of this in-VM Claude Code session is the login itself. When login completes, the participant exits it (`/exit` or Ctrl+D) and tells you. The credentials live inside this VM from now on and are never echoed or asked for again.

### 3. Continue setup from wherever you are

From here you continue with [in-vm-setup.md](in-vm-setup.md): toolchain, mock environment, workspace and clones. Those steps run the same commands whether you drive them from the host via the VM tool's shell wrapper or from inside the VM directly.

Optional: the participant may switch to a Claude Code session running inside the VM as the helper. If they want to switch, get the participant package into the VM first (the simplest way is to re-download it inside the VM, since it is a small public release):

```
cd ~
curl -L -o participant-package.zip \
    https://github.com/sdi2200262/bsc-apm-case-study-task/releases/download/participant-package/participant-package.zip
command -v unzip >/dev/null || { sudo apt-get update && sudo apt-get install -y unzip ; }
unzip participant-package.zip
```

Then have the participant open a Claude Code session at the package directory so the skill loads natively there:

```
cd ~/participant-package
claude
```

Hand them this paste-ready opening line for the new Claude Code session, then stop driving from the host:

> I'm a participant in the BSc APM Case Study. The helper skill is at `.claude/skills/bsc-apm-study-helper/` in this directory; please load it and continue setup from where the previous assistant left off. Run your state probe first: the toolchain, mock environment, and workspace may or may not already be set up.

If the participant stays with you on the host, no transfer is needed.

## Not handled here

- The toolchain (Docker, gcc, valgrind, uv, gh, etc.). That belongs to [in-vm-setup.md](in-vm-setup.md).
- The codebase clones. They live in the workspace, not in the participant-package directory; [in-vm-setup.md](in-vm-setup.md) creates the workspace and clones them.
- Starting a session. Sessions begin in [session.md](session.md), and only after the rest of setup is complete.
