#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) BSc APM Case Study 2025-2026

"""Copy Claude Code transcripts within a time range into a workspace folder.

Resolves the workspace path to its corresponding entry under
``~/.claude/projects/``, selects every ``.jsonl`` transcript whose first
record timestamp falls in the inclusive range ``[--from, --to]``, and
copies each into ``<workspace>/transcripts/``. For every selected
transcript, the sibling subdirectory named after the same session uuid
(``<projects>/<encoded>/<sessionId>/``) is also copied recursively to
``<workspace>/transcripts/<sessionId>/`` when present, preserving its
internal layout (typically ``subagents/`` and ``tool-results/``).

The encoding-based lookup can be overridden with ``--project-dir <name>``
(literal directory name under ``~/.claude/projects/``) for cases where
Claude Code's slugifier diverges from what the script computes locally.

Bad timestamps in ``--from`` or ``--to`` produce a clear error and a non
zero exit code without touching the filesystem. The destination directory
is never deleted; existing files inside it are kept (a per-file overwrite
prompt asks before replacement, unless ``--force`` is given). Existing
session subdirectories at the destination are merged into rather than
replaced; per-file overwrite inside a subdirectory is silent under
``--force`` and prompted otherwise.

Exit codes: ``0`` on success; ``1`` on input errors; ``2`` when the user
declines an overwrite prompt.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
DEST_DIRNAME = "transcripts"
NON_SLUG_CHARS = re.compile(r"[^A-Za-z0-9-]")


@dataclass(frozen=True)
class TimeRange:
    """Inclusive time range used to filter transcripts.

    Attributes:
        start: Lower bound, timezone-aware UTC.
        end: Upper bound, timezone-aware UTC.
    """

    start: datetime
    end: datetime


def encode_workspace(workspace: Path) -> str:
    """Encode an absolute workspace path the way Claude Code names project directories.

    Claude Code's slugifier replaces every character that is not an ASCII
    letter, digit, or hyphen with ``-``. That covers the path separator
    ``/`` and also ``.`` and ``_`` characters in usernames or directory
    names; the original rule that only handled ``/`` diverged on the
    first participant whose username contained a dot.

    Args:
        workspace: Resolved absolute workspace path.

    Returns:
        The encoded directory name.
    """
    return NON_SLUG_CHARS.sub("-", str(workspace))


def _tokenise(value: str) -> set[str]:
    """Split a string into lowercase alphanumeric tokens of length 2 or more.

    Hyphens, dots, underscores, and slashes are all treated as separators.
    Single-character tokens are dropped because they match too broadly.

    Args:
        value: Source string (a path segment or an encoded directory name).

    Returns:
        Set of lowercased tokens with length at least 2.
    """
    return {tok for tok in re.split(r"[^a-z0-9]+", value.lower()) if len(tok) >= 2}


def candidate_project_dirs(workspace: Path) -> list[Path]:
    """Find ``~/.claude/projects/`` entries that look related to ``workspace``.

    Used as a fallback when the encoded lookup misses. Tokenises the
    workspace path on every non-alphanumeric boundary, tokenises each
    project directory the same way, and ranks by the size of the token
    intersection. Two-or-more matching tokens are required; a single
    short overlap (e.g., everyone shares ``home``) is filtered out.

    Args:
        workspace: Resolved absolute workspace path.

    Returns:
        Project directory paths with at least two overlapping tokens,
        sorted by descending overlap then by name. Empty list when no
        ``~/.claude/projects/`` entry exists or no entry passes the
        threshold.
    """
    if not PROJECTS_ROOT.is_dir():
        return []
    workspace_tokens = _tokenise(str(workspace))
    if not workspace_tokens:
        return []
    scored: list[tuple[int, str, Path]] = []
    for entry in PROJECTS_ROOT.iterdir():
        if not entry.is_dir():
            continue
        overlap = workspace_tokens & _tokenise(entry.name)
        if len(overlap) >= 2:
            scored.append((len(overlap), entry.name, entry))
    scored.sort(key=lambda triple: (-triple[0], triple[1]))
    return [entry for _, _, entry in scored]


def resolve_project_dir(workspace: Path, override: str | None = None) -> Path:
    """Resolve a workspace path to its Claude Code project directory.

    When ``override`` is set, the function looks up that exact directory
    name under ``~/.claude/projects/`` and skips the encoding step. When
    the encoded lookup misses, the error message lists the closest
    matching directory names so the participant can re-run with
    ``--project-dir <name>``.

    Args:
        workspace: Workspace path supplied by the participant.
        override: Literal directory name under ``~/.claude/projects/``,
            bypassing the encoding step.

    Returns:
        Absolute path to ``~/.claude/projects/<encoded-or-override>``.

    Raises:
        FileNotFoundError: If the workspace path does not exist or the
            corresponding project directory does not exist.
    """
    if not workspace.exists():
        raise FileNotFoundError(f"workspace path does not exist: {workspace}")
    if not workspace.is_dir():
        raise FileNotFoundError(f"workspace path is not a directory: {workspace}")
    if override:
        project_dir = PROJECTS_ROOT / override
        if not project_dir.is_dir():
            raise FileNotFoundError(
                f"no Claude Code project directory at {project_dir}; "
                f"check the spelling against `ls {PROJECTS_ROOT}`"
            )
        return project_dir
    encoded = encode_workspace(workspace.resolve())
    project_dir = PROJECTS_ROOT / encoded
    if project_dir.is_dir():
        return project_dir
    candidates = candidate_project_dirs(workspace.resolve())
    hint_lines = [
        f"no Claude Code project directory found at {project_dir};",
        "Claude Code may have encoded this workspace path under a different name.",
    ]
    if candidates:
        hint_lines.append("Closest matches under ~/.claude/projects/:")
        for entry in candidates[:5]:
            hint_lines.append(f"  {entry.name}")
        hint_lines.append(
            "Re-run with --project-dir <name> using the matching directory above, "
            "or list the full set with `ls ~/.claude/projects/`."
        )
    else:
        hint_lines.append(
            "No related entries found. Has Claude Code been launched in "
            f"{workspace}? List ~/.claude/projects/ to confirm."
        )
    raise FileNotFoundError("\n".join(hint_lines))


def parse_iso(value: str, label: str) -> datetime:
    """Parse an ISO-8601 timestamp into a timezone-aware UTC ``datetime``.

    Accepts naive timestamps (treated as UTC), trailing ``Z``, and explicit
    offsets. Date-only inputs are accepted.

    Args:
        value: User-supplied timestamp string.
        label: Argument name used in the error message.

    Returns:
        Timezone-aware ``datetime`` in UTC.

    Raises:
        ValueError: If the input cannot be parsed as an ISO timestamp.
    """
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(
            f"{label}: not a valid ISO-8601 timestamp: {value!r} ({exc})"
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def first_timestamp(path: Path) -> datetime | None:
    """Read the first parseable record timestamp from a transcript file.

    Args:
        path: Absolute path to a ``.jsonl`` file.

    Returns:
        Timezone-aware UTC ``datetime``, or ``None`` if no usable timestamp
        was found.
    """
    import json

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            value = record.get("timestamp")
            if isinstance(value, str) and value:
                try:
                    return parse_iso(value, "transcript")
                except ValueError:
                    continue
    return None


def select_in_range(project_dir: Path, window: TimeRange) -> list[Path]:
    """Select transcripts whose first timestamp falls in ``window``.

    Args:
        project_dir: Resolved Claude Code project directory.
        window: Inclusive UTC time range.

    Returns:
        Paths sorted by first timestamp ascending.
    """
    selected: list[tuple[datetime, Path]] = []
    for path in sorted(project_dir.glob("*.jsonl")):
        ts = first_timestamp(path)
        if ts is None:
            continue
        if window.start <= ts <= window.end:
            selected.append((ts, path))
    selected.sort(key=lambda pair: pair[0])
    return [path for _, path in selected]


def confirm_overwrite(target: Path) -> bool:
    """Prompt the user before overwriting an existing destination file.

    Args:
        target: Destination path that already exists.

    Returns:
        ``True`` if the user confirms (``y``/``yes``), ``False`` otherwise.
    """
    answer = input(f"  overwrite existing {target.name}? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def copy_into_workspace(
    sources: list[Path],
    workspace: Path,
    force: bool,
) -> tuple[int, int, int]:
    """Copy transcripts into ``<workspace>/transcripts/``.

    Args:
        sources: Source transcript paths.
        workspace: Workspace path the participant supplied.
        force: When ``True``, overwrite without prompting.

    Returns:
        Tuple ``(copied, skipped, declined)``: counts of files newly written,
        files unchanged because the source equalled the destination, and
        files the user declined to overwrite.
    """
    dest_dir = workspace / DEST_DIRNAME
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    skipped = 0
    declined = 0
    for source in sources:
        target = dest_dir / source.name
        if target.exists():
            if not force and not confirm_overwrite(target):
                print(f"  skipped {source.name}")
                declined += 1
                continue
        shutil.copy2(source, target)
        print(f"  copied  {source.name}")
        copied += 1
    return copied, skipped, declined


def copy_session_subdirs(
    sources: list[Path],
    workspace: Path,
    force: bool,
) -> tuple[int, int]:
    """Copy each main transcript's sibling session subdirectory.

    For every source path, derives the session uuid from the file name
    (the stem of ``<sessionId>.jsonl``) and looks for a sibling directory
    of the same name in the source's parent. When present, the directory
    is copied recursively into
    ``<workspace>/transcripts/<sessionId>/``. Existing destination
    subdirectories are merged into rather than replaced; individual files
    inside a destination subdirectory follow the same overwrite rule as
    the top-level transcripts (per-file prompt unless ``--force``).

    Args:
        sources: Source transcript paths whose sibling subdirectories
            should be considered for copying.
        workspace: Workspace path the participant supplied.
        force: When ``True``, overwrite existing files inside destination
            subdirectories without prompting.

    Returns:
        Tuple ``(copied_dirs, missing_dirs)``: count of session
        subdirectories that existed at the source and were copied across,
        and count of selected sessions that had no sibling subdirectory
        on disk (the common case for sessions that did not dispatch any
        subagents and have no cached tool results).
    """
    dest_dir = workspace / DEST_DIRNAME
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing = 0
    for source in sources:
        session_id = source.stem
        sibling = source.parent / session_id
        if not sibling.is_dir():
            missing += 1
            continue
        target = dest_dir / session_id
        shutil.copytree(
            sibling,
            target,
            dirs_exist_ok=True,
            copy_function=_copy_with_overwrite_policy(force),
        )
        print(f"  copied  {session_id}/ (recursive)")
        copied += 1
    return copied, missing


def _copy_with_overwrite_policy(force: bool):
    """Return a ``shutil.copytree`` copy function that honours ``--force``.

    The returned callable matches the ``copy_function`` signature
    ``shutil.copytree`` expects: ``(src, dst)`` returning the destination
    path. When ``force`` is ``False`` and the destination already exists,
    the participant is prompted per file the same way top-level copies
    are; declined files are skipped without raising.

    Args:
        force: When ``True``, overwrite without prompting.

    Returns:
        A copy function suitable for ``shutil.copytree(..., copy_function=...)``.
    """
    def _copy(src: str, dst: str) -> str:
        target = Path(dst)
        if target.exists() and not force and not confirm_overwrite(target):
            print(f"    skipped {target.name}")
            return dst
        return shutil.copy2(src, dst)
    return _copy


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Copy Claude Code transcripts whose first record timestamp falls "
            "in [--from, --to] from ~/.claude/projects/<encoded>/ into "
            "<workspace>/transcripts/. For every selected transcript, the "
            "sibling session subdirectory of the same uuid is also copied "
            "recursively (carrying the subagents/ and tool-results/ content "
            "Claude Code wrote alongside the session). The destination "
            "directory is created if it does not exist; existing files "
            "prompt for overwrite unless --force is given."
        ),
        epilog=(
            "Examples:\n"
            "  collect-chats.py ~/work/eclass-mcp-server \\\n"
            "      --from 2026-05-01T09:00 --to 2026-05-01T12:30\n"
            "  collect-chats.py ~/work/eclass-mcp-server \\\n"
            "      --from 2026-05-01 --to 2026-05-02 --force"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "workspace",
        type=Path,
        help="Absolute path to the workspace directory Claude Code was launched in.",
    )
    parser.add_argument(
        "--from",
        dest="from_ts",
        required=True,
        help="Inclusive start of the time range (ISO-8601, naive treated as UTC).",
    )
    parser.add_argument(
        "--to",
        dest="to_ts",
        required=True,
        help="Inclusive end of the time range (ISO-8601, naive treated as UTC).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the destination without prompting.",
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help=(
            "Literal directory name under ~/.claude/projects/ to use, "
            "bypassing the encoded-path lookup. Use this when path encoding "
            "fails (e.g., the username contains characters Claude Code "
            "encodes differently than expected)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.

    Args:
        argv: Optional argument vector for testing.

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)
    try:
        start = parse_iso(args.from_ts, "--from")
        end = parse_iso(args.to_ts, "--to")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if start > end:
        print(
            f"error: --from ({start.isoformat()}) is after --to ({end.isoformat()})",
            file=sys.stderr,
        )
        return 1
    try:
        project_dir = resolve_project_dir(args.workspace, args.project_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    window = TimeRange(start=start, end=end)
    selected = select_in_range(project_dir, window)
    if not selected:
        print(
            f"No transcripts in {project_dir} with first timestamp in "
            f"[{start.isoformat()}, {end.isoformat()}].",
            file=sys.stderr,
        )
        return 0
    print(f"Copying {len(selected)} transcript(s) into {args.workspace / DEST_DIRNAME}:")
    copied, _, declined = copy_into_workspace(selected, args.workspace, args.force)
    copied_dirs, missing_dirs = copy_session_subdirs(selected, args.workspace, args.force)
    print(
        f"Done: {copied} transcript(s) copied, {declined} declined; "
        f"{copied_dirs} session subdirectory(ies) copied, "
        f"{missing_dirs} session(s) had none on disk."
    )
    return 2 if declined and copied == 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
