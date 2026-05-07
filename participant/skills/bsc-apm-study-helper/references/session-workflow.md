# Session workflow

A session has three phases: starting, working, and wrapping up. Between the two sessions, the participant runs the between-sessions reset described in the *Resetting between sessions* section of this file to return the workspace and the transcript store to the same state setup produced for session 1.

## Starting a session

Note the wall-clock start time, then open Claude Code with the workspace as its working directory. Each framework (APM or Spec-kit, as assigned for this session) has its own way of starting; follow the assigned framework's documentation and point it at `PROMPT.md` as the task.

## Working on the task

Work for up to three hours and stop at the three-hour mark whether or not the task is finished. Use only the framework assigned to the current session and follow its documented workflow as written; the study compares each framework as its documentation describes it. The helper scripts run only between or after sessions; the `.jsonl` files in the workspace's transcript directory accumulate untouched throughout the session and are collected at the end as part of the submission.

## Wrapping up

**1. Create the patch.** From inside the implementation codebase, stage every change (including new files) and diff against the pinned commit. The `--cached` flag is what pulls newly created source files into the diff, even when the working tree is otherwise clean.

```
cd <workspace>/eclass-mcp-server
git add -A
git diff --cached dbd2d16 > ../solution.patch
```

**2. Collect the transcripts.** Claude Code stores transcripts under `~/.claude/projects/` in a per-workspace subdirectory whose name is the workspace's absolute path with every character that is not an ASCII letter, digit, or hyphen replaced by `-`. The path separator `/`, the dot `.`, and the underscore `_` all get replaced; usernames or directory names containing those characters are normalised the same way. List what is in the workspace's transcript directory and pick the rows that belong to the session just finished; the `--from-projects` flag tells `list-chats.py` to resolve the mapping:

```
python3 /path/to/scripts/list-chats.py \
    <workspace> --from-projects
```

The script prints one row per transcript with first and last record timestamps and a preview of the first user message. Copy the matching rows out with `collect-chats.py`, pasting the timestamps verbatim into `--from` and `--to` (slightly widen the window to be inclusive):

```
python3 /path/to/scripts/collect-chats.py <workspace> \
    --from 2026-05-01T09:00 --to 2026-05-01T12:30
```

The script copies the matching transcripts into `<workspace>/transcripts/`. For every selected transcript, the script also copies the sibling per-session subdirectory of the same uuid (`subagents/` and `tool-results/` inside it) recursively into `<workspace>/transcripts/<sessionId>/`; sessions that did not dispatch any subagents and have no cached tool results have no such subdirectory and the script silently skips them. The closing line reports `N session(s) had none on disk` for those; that is a normal report, not an error. Verify the contents of that directory by re-running `list-chats.py` against it with `--from-dir`, which scans the directory directly instead of resolving a workspace path. The listing enumerates the top-level main transcripts only; the per-session subdirectories ride along with their main transcript.

```
python3 /path/to/scripts/list-chats.py \
    <workspace>/transcripts --from-dir
```

The output should match the rows the participant intended to collect, with the same first and last timestamps. If a row is missing, widen the time window and re-run `collect-chats.py`.

**Manual fallback when path encoding fails.** If `list-chats.py`, `collect-chats.py`, or `reset-cc-project.py` reports `no Claude Code project directory found at ...`, the script's encoded name does not match what Claude Code wrote on disk for this workspace. The error message lists the closest matches under `~/.claude/projects/`. Run `ls ~/.claude/projects/` to see the full set, identify the directory belonging to this workspace, and re-run the script with `--project-dir=<name>` (use the `=` form because the encoded names start with `-` and would otherwise be parsed as another flag):

```
python3 /path/to/scripts/list-chats.py <workspace> --from-projects \
    --project-dir=-home-username-workspace
```

The same `--project-dir` flag is accepted by `collect-chats.py` and `reset-cc-project.py`.

**3. Package the submission.** Zip `solution.patch` and `transcripts/` together at the workspace root. The filename uses the participant ID, the session number, and the framework used in this session:

```
cd <workspace>
zip -r P001_S1_apm.zip solution.patch transcripts/
```

The zip contains exactly two entries at its root: `solution.patch` and `transcripts/`. Inside `transcripts/`, the top-level entries are one `.jsonl` per main session and one subdirectory per session named after the same session uuid; each subdirectory holds the `subagents/` and `tool-results/` content Claude Code wrote alongside that session. Sessions that produced no subagent dispatches and no cached tool results have no subdirectory.

**4. Move the zip out of the workspace.** The between-sessions reset wipes everything in the workspace, including the zip. Store it in a directory outside the workspace and outside the participant package; `~/Documents/bsc-apm-submissions/` is a reasonable default. Both session zips end up there, and the cleanup commands later leave that directory untouched.

```
mkdir -p ~/Documents/bsc-apm-submissions
mv <workspace>/P001_S1_apm.zip ~/Documents/bsc-apm-submissions/
```

**5. Submit the form.** Open the submission form (URL in the participant guide; if not on hand, refer the participant to the study contact). Fill in the per-session questions and attach the zip just stored. Do this immediately after wrapping up, while the session is fresh.

## Resetting between sessions

Run this after the first session has wrapped up and before the second session starts. Before running any of the steps below, confirm that session 1's submission zip is in the safe-storage directory (e.g., `ls -la ~/Documents/bsc-apm-submissions/` should list `P001_S1_*.zip`); the reset is destructive and only zips outside the workspace survive. Once that is confirmed, the reset returns the workspace and the transcript store to the same state setup produced for session 1, so session 2 begins from an identical baseline. The mock environment is left alone unless there is a reason to believe it has drifted from its initial state.

**1. Reset the implementation codebase.** From inside `eclass-mcp-server`, hard-reset to the pinned commit, wipe untracked and ignored files, and rebuild the virtual environment from scratch:

```
cd <workspace>/eclass-mcp-server
git reset --hard dbd2d16
git clean -fdx
uv sync --dev --all-extras
```

`git clean -fdx` removes every untracked file, including ignored files such as `.venv/` and any `__pycache__/` directories. Re-copy `.env` and `certs/` from the mock-environment prefix afterwards (see [mock-environment.md](mock-environment.md), MCP server configuration); they are removed by `git clean`.

**2. Reset the reference codebase.** Restore `openeclass` to its pinned commit and a clean working tree:

```
cd <workspace>/openeclass
git reset --hard e8b3329
git clean -fdx
```

**3. Sweep the workspace.** Confirm the workspace root contains exactly four entries: `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, and `openeclass/`.

```
ls -la <workspace>
```

Delete any extra files or directories the AI may have created at the workspace root. If `PRD.md` or `PROMPT.md` were modified during the session, restore them from the participant package's `task/` directory; session 2 must read them in their original form.

**4. Wipe the Claude Code project state for this workspace.** Remove the workspace's entry under `~/.claude/projects/` in full so session 2 starts from a clean baseline; the script touches only that workspace's project directory:

```
python3 /path/to/scripts/reset-cc-project.py <workspace>
```

The script inventories the directory's contents (top-level transcripts, per-session subdirectories, the project-local `memory/` store, anything else Claude Code has cached) and asks for confirmation. Run it only after the session's zip has been safely stored; the deletion is permanent. Claude Code recreates the project directory on the next launch.

**5. Reset the mock environment, only if needed.** The mock environment retains its initial state across sessions and usually does not need a reset. Reset it only if a previous session modified the test data:

```
cd <mock>
./scripts/reset
```

**6. Confirm the baseline.** After the reset, confirm the workspace and the transcript store match the same state setup produced for session 1:

- `<mock>/scripts/status` reports every service ok.
- `<workspace>/eclass-mcp-server` is at `dbd2d16` with a clean working tree.
- `<workspace>/openeclass` is at `e8b3329` with a clean working tree.
- The workspace root contains `PRD.md`, `PROMPT.md`, `eclass-mcp-server/`, and `openeclass/`, and nothing else; `PRD.md` and `PROMPT.md` match their original contents from the participant package.
- The workspace's Claude Code project directory under `~/.claude/projects/` either does not yet exist or has been freshly created with no session-1 state inside.

Once the baseline is in place, the participant returns to *Starting a session* and repeats the same starting-working-wrapping-up flow for session 2 (with the other assigned framework). Session 2 ends after step 5 of *Wrapping up* (*Submit the form*); the resetting steps are not needed to be run again.

## Cleaning up

Optional. Once both session zips have been submitted (see [submission.md](submission.md)), nothing in the study needs to stay on the participant's machine. Before running any cleanup command, list the contents of the safe-storage directory and confirm both `P001_S1_*.zip` and `P001_S2_*.zip` are present (or the equivalents the participant submitted); the cleanup steps below leave that directory untouched.

For a clean slate:

- Wipe session 2's Claude Code project state: `python3 /path/to/scripts/reset-cc-project.py <workspace>`.
- Delete the workspace: `rm -rf <workspace>`.
- Uninstall the mock environment: follow the steps in [mock-environment.md](mock-environment.md), Uninstall.

The participant package itself can be deleted at this point as well; it has no further role. The safe-storage directory and its contents are kept.
