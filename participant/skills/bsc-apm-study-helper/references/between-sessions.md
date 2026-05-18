# Between sessions

You are here because the participant has wrapped up the first session and is preparing for the second. This has two parts with different timing. The baseline reset (steps 1 to 4) returns the workspace and the transcript store to the same state in-VM setup produced for session 1; it can be run any time after session 1 wraps. The mock reseed (step 5) refreshes the test data so its dates are current, and must be run immediately before session 2 starts, even when steps 1 to 4 were done earlier. A participant who resets right after session 1 and returns days later for session 2 still runs step 5 at that point.

Before any of the steps below, confirm session 1's submission zip is in the safe-storage directory. The reset is destructive; only zips outside the workspace survive:

```
ls -la ~/Documents/bsc-apm-submissions/
```

The listing should include `<PID>_S1_<framework>.zip`. If it does not, stop and resolve that first; the zip cannot be recovered after the reset.

## 1. Reset the implementation codebase

From inside `eclass-mcp-server`, hard-reset to the pinned commit, wipe untracked and ignored files, rebuild the virtual environment from scratch:

```
cd <workspace>/eclass-mcp-server
git reset --hard dbd2d16
git clean -fdx
uv sync --dev --all-extras
```

`git clean -fdx` removes every untracked file, including ignored files such as `.venv/` and any `__pycache__/` directories. Re-copy `.env` and `certs/` from the mock-environment prefix afterwards (see [in-vm-setup.md](in-vm-setup.md), MCP server configuration); they are removed by `git clean`.

## 2. Reset the reference codebase

Restore `openeclass` to its pinned release `Release_4.3.3` and a clean working tree:

```
cd <workspace>/openeclass
git reset --hard Release_4.3.3
git clean -fdx
```

## 3. List the workspace contents

Confirm the workspace root contains exactly four entries: `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, `openeclass/`:

```
ls -la <workspace>
```

Delete any extra files or directories the AI may have created at the workspace root. If `PRD.md` or `PROMPT.md` were modified during the session, restore them the same way they were dropped into the workspace during in-VM setup (see [in-vm-setup.md](in-vm-setup.md), Workspace and codebases). Session 2 must read both in their original form.

## 4. Wipe the Claude Code project state

Remove the workspace's entry under `~/.claude/projects/` so session 2 starts from a clean baseline. The directory contains transcripts, per-session subdirectories, the project-local `memory/` store, and anything else Claude Code has cached for this workspace; the deletion is permanent.

```
ls ~/.claude/projects/
```

Identify the entry that matches the workspace path. Inventory its contents in plain words for the participant before removing:

```
ls -la ~/.claude/projects/<encoded>/
rm -rf ~/.claude/projects/<encoded>/
```

Run the `rm` only after the session's zip has been safely stored. Claude Code recreates the project directory on the next launch.

## 5. Reseed the mock environment, immediately before session 2

Run this as the last step before session 2 starts, not earlier. The mock's test data is dated relative to when it was loaded, so session 2 must run against a freshly loaded set. Run it even when steps 1 to 4 were done earlier, and even when no session modified the test data:

```
cd <mock>
./scripts/reset
```

`./scripts/reset` is a single self-contained command: it stops the stack, drops its data volumes, and brings everything back up with the test data reloaded, so its dates are current as of session 2's start. No separate `./scripts/down` or `./scripts/up` is needed around it. It does not touch `<mock>/.env` or `<mock>/certs/`, so the MCP wiring set up earlier still holds. The reload takes a few minutes and runs before session 2's wall-clock start, so it does not count against the session time.

## 6. Confirm the baseline

After the reset, confirm the workspace and the transcript store match the same state in-VM setup produced for session 1:

- `<mock>/scripts/status` reports every service ok, with the test data just reloaded by step 5.
- `<workspace>/eclass-mcp-server` is at `dbd2d16` with a clean working tree.
- `<workspace>/openeclass` is at `Release_4.3.3` with a clean working tree.
- The workspace root contains `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, `openeclass/`, and nothing else; `PRD.md` and `PROMPT.md` match their original contents from the participant package.
- The workspace's Claude Code project directory under `~/.claude/projects/` either does not yet exist or has been freshly created with no session-1 state inside.

With the reseed just run, the participant returns to [session.md](session.md) and begins session 2 promptly (with the other assigned framework) so the test data stays current. Session 2 ends at *Wrapping up*, step 5 (*Submit the form*); the resetting steps are not run again.
