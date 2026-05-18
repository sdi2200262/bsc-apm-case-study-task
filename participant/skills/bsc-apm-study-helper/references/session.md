# Session

You are here because the participant is about to start a session, is mid-session and asking about something that cannot wait, or is wrapping up a session that has just ended.

## Before starting

Each session uses one of two AI-assisted development frameworks: APM or Spec-kit. The participant has been told privately by the coordinator which framework is assigned to which session; you have not been told, and don't retain that across sessions. Before any framework-specific step, ask the participant which framework is assigned to this session and wait for the answer. The two frameworks have different install models (APM ships as an npm package installed globally; Spec-kit is invoked via `uvx` from a release tag on every call, with no persistent install needed), so follow the framework-specific subsection below for whichever is assigned. The framework's own workspace bootstrap runs at session start, covered below in *Starting a session*.

### Agentic Project Management (APM)

APM (https://agentic-project-management.dev) ships as an npm package; the CLI is invoked as `apm`.

```
sudo npm install -g agentic-pm
apm --version
```

### GitHub Spec-kit

Spec-kit (https://github.github.io/spec-kit/) runs through `uvx` from a release tag of the upstream repository; the CLI is invoked as `specify`, prefixed by the same `uvx --from` expression on every invocation. The study does not pin a specific tag: open https://github.com/github/spec-kit/releases, pick the current release, and use that tag for every Spec-kit command in this session. `v0.8.5` is the floor verified for the study; anything newer is fine.

```
uvx --from git+https://github.com/github/spec-kit.git@<tag> \
    specify --help
```

`<tag>` is the release tag picked from the releases page above (e.g. the current `v0.8.x`).

## Quick task summary

Before the participant crosses into the workspace, give them a short summary of what they will build, then close the door on further task questions and send them to read the PRD and PROMPT themselves.

Keep the summary small. In one or two sentences, name what the task is: the participant extends the Python `eclass-mcp-server` with two new announcement tools (`get_course_announcements` and `get_general_announcements`) and produces a standalone C replica at `eclass-mcp-server/c-replica/` that exposes all six tools (the four baseline tools plus the two new ones) and behaves as a drop-in replacement for the Python server. `PRD.md` is the single source of truth, and submissions are validated and evaluated against exactly what it specifies.

In one short paragraph, tie the scaffolding to what the task integrates against. The running mock environment in the workspace is the same openeclass platform the participant cloned read-only into `<workspace>/openeclass/`, packaged as a docker image at the same pinned release; reading the `openeclass/` tree is the most direct way to understand how the live mock behaves. The mock is what the implementation integrates against during the session, what the participant validates the implementation against as they go, and the same surface the post-session evaluation runs against. The `eclass-mcp-server/` checkout in the workspace is what gets extended; `solution.patch` at wrap-up is the diff against the pinned baseline `dbd2d16`.

After the summary, stop. Tell the participant you can't add more on the task content itself and they should read `<workspace>/PRD.md` and `<workspace>/PROMPT.md` in full before the session starts. The two files together are the canonical task description; do not split them across different question types or present them as serving different purposes.

## Starting a session

For session 2, the mock reseed in [between-sessions.md](between-sessions.md) (step 5) must have just been run. If the between-sessions baseline reset was done earlier and time has passed since, run that reseed again now, before the first message, so the mock's test data is current as of session 2's start.

The session begins the moment the participant sends their first message in the workspace Claude Code session. Launching `claude` and reading the PRD or PROMPT inside it is still pre-work; the wall-clock start time is the timestamp on that first message, not the moment `claude` is launched.

Getting to the workspace Claude Code needs an interactive VM shell, because the framework's workspace bootstrap is interactive and `claude` itself wants a real terminal. Where you're running now decides what the participant does next:

- If you are running on the host (driving the VM through `limactl shell task -- ...` or `wsl -d task -- ...`), the participant opens a separate interactive VM shell themselves: `limactl shell task` or the WSL2 shell (`wsl -d task`).
- If you are running inside the VM as a Claude Code session at the participant-package directory, the participant exits that session (`/exit` or `Ctrl+D`) from their terminal and stays in the same shell.

From that interactive VM shell, the participant changes into the workspace and runs the assigned framework's workspace bootstrap. The framework's interactive setup takes over from there; the framework's documentation covers what to choose during bootstrap and the rest of the workflow.

For APM:

```
cd <workspace>
apm init
```

For Spec-kit (use the same `<tag>` chosen at install time; `--here` initialises in the existing workspace rather than creating a new subdirectory):

```
cd <workspace>
uvx --from git+https://github.com/github/spec-kit.git@<tag> \
    specify init --here
```

Once the bootstrap completes, the participant starts Claude Code from the same workspace shell:

```
claude
```

This workspace Claude Code session does not load the helper skill; the implementation work runs unassisted.

Each framework opens its session with a specific slash command. Tell the participant the first command for their assigned framework, then point them at the framework's documentation for the rest of the workflow.

For APM, the first message is:

```
/apm-1-initiate-planner @PROMPT.md
```

`@PROMPT.md` is a Claude Code file reference that passes the workspace's `PROMPT.md` as the task context to the Planner. The rest of the APM workflow is at https://agentic-project-management.dev/docs/.

For Spec-kit, the first message is:

```
/speckit.constitution
```

`PROMPT.md` is supplied later in the workflow at the `/speckit.specify` step rather than at the constitution step. The Spec-kit workflow documentation is at https://github.github.io/spec-kit/.

The session's wall-clock start time is the timestamp on the first message the participant sends, whichever framework they are using.

## Working on the task

Work for up to three hours and stop at the three-hour mark whether or not the task is finished. Use only the framework assigned to the current session and follow its documented workflow as written; the study compares each framework as its documentation describes it.

The transcripts accumulate untouched throughout the session in `~/.claude/projects/<encoded>/`, where `<encoded>` is the workspace's absolute path with every character that is not an ASCII letter, digit, or hyphen replaced by `-` (the path separator `/`, the dot `.`, the underscore `_` all get replaced). The participant does not list, edit, or delete those files during the session; they are collected at the end as part of the submission.

If a logistics emergency surfaces during the session (mock environment crashed, ports got bound by another service, the framework's CLI is producing an unexplained error before any task work has happened), the participant can step back to you in their other window (the host AI or the in-VM Claude Code at the participant-package directory, whichever they have running) and ask for help. For anything else, redirect: in-session, the participant relies on the assigned framework, not on you.

## Wrapping up

### 1. Create the patch

From inside the implementation codebase, stage every change (including new files) and diff against the pinned commit. The `--cached` flag is what pulls newly created source files into the diff, even when the working tree is otherwise clean.

```
cd <workspace>/eclass-mcp-server
git add -A
git diff --cached dbd2d16 > ../solution.patch
```

### 2. Collect the transcripts

List the entries under `~/.claude/projects/`. The directory name encodes the workspace path per the rule above (path separator and dots and underscores all replaced by `-`):

```
ls ~/.claude/projects/
```

Identify the entry that matches the workspace; substring overlap with the workspace path is the cue. From that entry, list the transcripts and inspect their first and last record timestamps to identify which transcripts belong to the session that just ended. The participant's wall-clock note for when the session started is the cross-check; transcripts whose first record timestamp falls inside the session window belong to the session.

```
ls -la ~/.claude/projects/<encoded>/*.jsonl
head -1 ~/.claude/projects/<encoded>/<sessionId>.jsonl
tail -1 ~/.claude/projects/<encoded>/<sessionId>.jsonl
```

For each matching transcript, copy the `.jsonl` and the sibling per-session subdirectory of the same uuid (carrying the `subagents/` and `tool-results/` records Claude Code wrote alongside that session) into `<workspace>/transcripts/`. Sessions that did not dispatch any subagents and have no cached tool results have no such subdirectory; copy only the `.jsonl` for those, and that is the correct shape:

```
mkdir -p <workspace>/transcripts
cp ~/.claude/projects/<encoded>/<sessionId>.jsonl <workspace>/transcripts/
cp -r ~/.claude/projects/<encoded>/<sessionId>/ <workspace>/transcripts/<sessionId>/
```

The third command runs only when `~/.claude/projects/<encoded>/<sessionId>/` exists; check with `ls -d ~/.claude/projects/<encoded>/<sessionId>/` first.

Repeat the `cp` and `cp -r` for every transcript that belongs to the session. Verify the result:

```
ls -la <workspace>/transcripts
```

The directory should contain one `.jsonl` per main session of the just-ended session and, optionally, one `<sessionId>/` subdirectory per session that dispatched subagents.

### 3. Package the submission

Zip `solution.patch` and `transcripts/` together at the workspace root. The filename follows the pattern `<PID>_S<n>_<framework>.zip`, where `<PID>` is the participant ID, `<n>` is `1` or `2`, and `<framework>` is `apm` or `speckit` for this session. For participant P001's session 1 with APM, that is `P001_S1_apm.zip`:

```
cd <workspace>
zip -r <PID>_S<n>_<framework>.zip solution.patch transcripts/
```

The zip contains exactly two entries at its root: `solution.patch` and `transcripts/`. Inside `transcripts/`, the top-level entries are one `.jsonl` per main session and one subdirectory per session that dispatched subagents (named after the session uuid).

### 4. Move the zip out of the workspace

The between-sessions reset wipes everything in the workspace, including the zip. Store it in a directory outside the workspace and outside the participant package; `~/Documents/bsc-apm-submissions/` is a reasonable default:

```
mkdir -p ~/Documents/bsc-apm-submissions
mv <workspace>/<PID>_S<n>_<framework>.zip ~/Documents/bsc-apm-submissions/
```

Both session zips end up there, and the cleanup commands later leave that directory untouched.

### 5. Submit the form

Open the per-session submission form. Fill in the per-session questions and attach the zip just stored. Do this immediately after wrapping up, while the session is fresh.

The form URL is given in the participant guide's wrap-up section. If the participant does not have it to hand, refer them to the study contact.

### Submission checklist

- Session 1: form submitted with `<PID>_S1_<framework>.zip` attached.
- Session 2: form submitted with `<PID>_S2_<framework>.zip` attached, framework swapped.
