# Session

You are here because the participant is about to start a session, is mid-session and asking about something that cannot wait, or is wrapping up a session that has just ended.

## Before starting

Each session uses one of two AI-assisted development frameworks: APM or Spec-kit. The participant has been told privately by the coordinator which framework is assigned to which session; the helper has not, and does not retain across sessions. Before any framework-specific step, ask the participant which framework is assigned to this session and wait for the answer. The two frameworks have different install models (APM ships as an npm package installed globally; Spec-kit is invoked via `uvx` from a release tag on every call, with no persistent install needed), so follow the framework-specific subsection below for whichever is assigned. The framework's own workspace bootstrap runs at session start, covered below in *Starting a session*.

### Agentic Project Management (APM)

APM (https://agentic-project-management.dev) ships as an npm package; the CLI is invoked as `apm`.

```
sudo npm install -g agentic-pm
apm --version
```

### GitHub Spec-kit

Spec-kit (https://github.github.io/spec-kit/) runs through `uvx` from a release tag of the upstream repository; the CLI is invoked as `specify`, prefixed by the same `uvx --from` expression on every invocation. The study does not pin a specific tag: open https://github.com/github/spec-kit/releases, pick the current release, and use that tag for every Spec-kit command in this session. `v0.8.3` is the floor verified for the study; anything newer is fine.

```
uvx --from git+https://github.com/github/spec-kit.git@<tag> \
    specify --help
```

`<tag>` is the release tag picked from the releases page above (e.g. the current `v0.8.x`).

## Orient before starting

Before the participant crosses into the workspace, give them a short orientation to what they will build, then close the door on further task questions and send them to read the PRD and PROMPT themselves.

The orientation stays small. In one or two sentences, name what the task is: the participant extends the Python `eclass-mcp-server` with two new announcement tools (`get_course_announcements` and `get_general_announcements`), and produces a standalone C replica at `eclass-mcp-server/c-replica/` that exposes all six tools (the four baseline tools plus the two new ones) and behaves as a drop-in replacement for the Python server. `PRD.md` is the single source of truth: submissions are validated and evaluated against exactly what the PRD specifies, against the same mock environment the participant has running locally.

In one short paragraph, tie the scaffolding to what comes next: the running mock environment is the system the implementation integrates against and the same surface the post-session evaluation runs against, so testing and iterating against it during the session is the most direct way to check the implementation; the `eclass-mcp-server/` checkout in the workspace is what gets extended; the `openeclass/` checkout is the read-only PHP reference; `solution.patch` at wrap-up is the diff against the pinned baseline `dbd2d16`.

After the orientation, do not answer further questions about what the task entails, what the requirements are, what acceptance looks like, or how to interpret any part of the PRD or PROMPT. Redirect to `<workspace>/PRD.md` for the requirements and `<workspace>/PROMPT.md` for the opening prompt; the participant reads both before the session starts. Logistics questions (where files are, how to start the framework, how to wrap up) stay in scope; task-content questions go to the PRD.

## Starting a session

Note the wall-clock start time. The helper Claude Code session running this skill is project-scoped to the participant-package directory; to switch into the workspace, the participant exits the helper, opens a fresh shell, runs the assigned framework's bootstrap in the workspace, then starts a new Claude Code session there:

```
# in the helper terminal:
/exit       # or press Ctrl+D

# then in a fresh shell:
cd <workspace>
```

From the workspace shell, run the assigned framework's workspace bootstrap. The framework's own interactive setup takes over from here; consult the framework's documentation for what to choose during bootstrap and for the rest of the workflow.

For APM:

```
apm init
```

For Spec-kit (use the same `<tag>` chosen at install time; `--here` initialises in the existing workspace rather than creating a new subdirectory):

```
uvx --from git+https://github.com/github/spec-kit.git@<tag> \
    specify init --here
```

Once the bootstrap completes, start Claude Code from the same workspace shell:

```
claude
```

The workspace's Claude Code session does not load this skill, by design: the implementation work is unassisted by the helper. With the framework bootstrapped, follow the framework's documentation for how it expects to be driven, and point it at `PROMPT.md` as the task.

## Working on the task

Work for up to three hours and stop at the three-hour mark whether or not the task is finished. Use only the framework assigned to the current session and follow its documented workflow as written; the study compares each framework as its documentation describes it.

The transcripts accumulate untouched throughout the session in `~/.claude/projects/<encoded>/`, where `<encoded>` is the workspace's absolute path with every character that is not an ASCII letter, digit, or hyphen replaced by `-` (the path separator `/`, the dot `.`, the underscore `_` all get replaced). The participant does not list, edit, or delete those files during the session; they are collected at the end as part of the submission.

If a logistics emergency surfaces during the session (mock environment crashed, ports got bound by another service, the framework's CLI is producing an unexplained error before any task work has happened), the participant can switch to the participant-package Claude Code session in another shell and consult the helper. For anything else, redirect: in-session, the participant relies on the assigned framework, not the helper.

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
