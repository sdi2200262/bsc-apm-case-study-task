# Participant Materials

Source for the participant package release. The contents of this directory bundle into `participant-package.zip` (the `participant-package` release tag); together with the testing environment release tarballs that ship from the same repository's `bsc-apm-case-study-task` and `bsc-apm-case-study-task-arm64` tags, they cover everything a participant uses end to end.

## Contents

| Path | Description |
|------|-------------|
| [`guide/`](guide/) | Participation guide (LaTeX source, compiled PDF, build assets) |
| [`task/PRD.md`](task/PRD.md) | Product Requirements Document; the single source of truth for the implementation |
| [`task/PROMPT.md`](task/PROMPT.md) | Default prompt to start the AI assistant conversation |
| [`task/README.txt`](task/README.txt) | Throwaway one-shot setup notes carrying the clone commands; the participant deletes this after setup |
| [`scripts/`](scripts/) | Helper scripts for managing Claude Code transcripts during a session |
| [`skills/bsc-apm-study-helper/`](skills/bsc-apm-study-helper/) | Optional Claude Code skill the participant package ships pre-extracted |

## Task Overview

*Announcements Functionality and C Replica*

Participants are tasked with:

1. Implementing `get_course_announcements` and `get_general_announcements` tools in the existing Python MCP server, `eclass-mcp-server`.
2. Creating a native C replica of the entire MCP server inside `eclass-mcp-server/c-replica`.

## Key Challenges

- **Legacy-codebase research**: The retrieval logic for the new tools is not present in the existing `eclass-mcp-server`; participants research `openeclass/` to derive the data path their implementations follow.
- **Date filtering**: The new tools accept a `days_back` parameter; participants design and implement the filtering logic and validation rules per the PRD.
- **C implementation**:
    - Manual JSON-RPC 2.0 framing, parsing, and serialisation; no JSON-parsing library is permitted.
    - Networking and HTML or XML parsing through the libraries the PRD names.
- **Memory safety**: The C replica must be free of detectable leaks under `valgrind` across its supported tool-session surface.

## Helper Scripts

The three Python scripts in [`scripts/`](scripts/) manage Claude Code transcripts. Each script accepts the workspace path as its positional argument and resolves it to the corresponding entry under `~/.claude/projects/`.

| Script | Purpose |
|--------|---------|
| `list-chats.py` | List transcripts in a workspace's project directory with first and last record timestamps and a preview of the first user message. |
| `collect-chats.py` | Copy transcripts whose first record timestamp falls in a given ISO time range into `<workspace>/transcripts/`. |
| `reset-cc-project.py` | Remove the workspace's entry under `~/.claude/projects/` in full (transcripts, per-session subdirectories, project-local `memory/`, anything else Claude Code has cached). Destructive; prompts for confirmation by default. |

Run any script with `--help` for usage and examples.

## Building the guide

The guide PDF (`guide/participant-guide-cc.pdf`) is committed to the repository and copied into the participant-package zip at release time. To rebuild it locally, run:

```bash
make participant-guide
```

from the repository root, which invokes `latexmk -pdf` per the configuration in `guide/latexmkrc`. Auxiliary files land in `guide/build/` (gitignored) and the rebuilt PDF is copied back to `guide/` after a successful compilation. To clean the auxiliary build directory, run `latexmk -c` from inside `guide/`.

## Related

- [Participation guide](guide/) - the document participants follow end to end
- [bsc-apm-case-study-infra](https://github.com/sdi2200262/bsc-apm-case-study-infra) - grader, parser, scoring rubric, and evaluation pipeline (separate repository)
