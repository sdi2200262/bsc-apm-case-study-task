# Between sessions

You are here because the participant has wrapped up the first session and is about to start the second. The destructive reset returns the workspace and the transcript store to the same state in-VM setup produced for session 1, so session 2 begins from an identical baseline.

Before any of the steps below, confirm session 1's submission zip is in the safe-storage directory. The reset is destructive; only zips outside the workspace survive:

```
ls -la ~/Documents/bsc-apm-submissions/
```

The listing should include `<PID>_S1_<framework>.zip`. If it does not, stop and resolve that first; the zip cannot be recovered after the reset.

The mock environment is left alone unless there is a reason to believe it has drifted from its initial state.

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

Restore `openeclass` to its pinned commit and a clean working tree:

```
cd <workspace>/openeclass
git reset --hard e8b3329
git clean -fdx
```

## 3. List the workspace contents

Confirm the workspace root contains exactly four entries: `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, `openeclass/`:

```
ls -la <workspace>
```

Delete any extra files or directories the AI may have created at the workspace root. If `PRD.md` or `PROMPT.md` were modified during the session, restore them from the participant package's `task/` directory; session 2 must read them in their original form.

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

## 5. Reset the mock environment, only if needed

The mock environment retains its initial state across sessions and usually does not need a reset. Reset it only if a previous session modified the test data:

```
cd <mock>
./scripts/reset
```

## 6. Confirm the baseline

After the reset, confirm the workspace and the transcript store match the same state in-VM setup produced for session 1:

- `<mock>/scripts/status` reports every service ok.
- `<workspace>/eclass-mcp-server` is at `dbd2d16` with a clean working tree.
- `<workspace>/openeclass` is at `e8b3329` with a clean working tree.
- The workspace root contains `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, `openeclass/`, and nothing else; `PRD.md` and `PROMPT.md` match their original contents from the participant package.
- The workspace's Claude Code project directory under `~/.claude/projects/` either does not yet exist or has been freshly created with no session-1 state inside.

Once the baseline is in place, the participant returns to [session.md](session.md) for session 2 (with the other assigned framework). Session 2 ends at *Wrapping up*, step 5 (*Submit the form*); the resetting steps are not run again.
