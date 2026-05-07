#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) BSc APM Case Study 2025-2026

"""Delete every Claude Code project file for a workspace.

Resolves the workspace path to its corresponding entry under
``~/.claude/projects/`` and removes the entire directory tree at that
path: top-level ``.jsonl`` transcripts, every per-session subdirectory
(``<sessionId>/`` containing ``subagents/`` and ``tool-results/``), the
project-local ``memory/`` store, and anything else Claude Code has
cached for that workspace. Claude Code recreates the directory on the
next launch, so session 2 starts from a fully clean baseline.

The encoding-based lookup can be overridden with ``--project-dir <name>``
(literal directory name under ``~/.claude/projects/``) for cases where
Claude Code's slugifier diverges from what the script computes locally.

This action is destructive. By default it inventories the directory's
contents and prompts for confirmation. Pass ``--force`` to skip the
prompt; the inventory still prints so the action stays observable.

Exit codes: ``0`` on a successful deletion or a confirmed no-op; ``1``
on input errors; ``2`` when the user declines the prompt.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
NON_SLUG_CHARS = re.compile(r"[^A-Za-z0-9-]")


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


def inventory_project_dir(project_dir: Path) -> tuple[list[Path], list[Path]]:
    """List the top-level files and subdirectories of a project directory.

    Args:
        project_dir: Resolved Claude Code project directory.

    Returns:
        Tuple ``(files, subdirs)``: top-level file paths sorted by name,
        and top-level subdirectory paths sorted by name.
    """
    files = sorted(p for p in project_dir.iterdir() if p.is_file())
    subdirs = sorted(p for p in project_dir.iterdir() if p.is_dir())
    return files, subdirs


def confirm(prompt: str) -> bool:
    """Prompt for an interactive yes/no confirmation.

    Args:
        prompt: Text shown to the user.

    Returns:
        ``True`` if the user answers ``y``/``yes``, ``False`` otherwise.
    """
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def delete_project_dir(project_dir: Path) -> bool:
    """Remove the entire project directory tree.

    Args:
        project_dir: Resolved Claude Code project directory to delete.

    Returns:
        ``True`` on success, ``False`` if the removal failed (the error
        is printed to stderr).
    """
    try:
        shutil.rmtree(project_dir)
        return True
    except OSError as exc:
        print(f"error: failed to remove {project_dir} ({exc})", file=sys.stderr)
        return False


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Delete every Claude Code project file for a workspace. "
            "Resolves the workspace path to its ~/.claude/projects/ entry "
            "and removes the entire directory tree at that path: top-level "
            ".jsonl transcripts, per-session subdirectories (subagents/ "
            "and tool-results/), the project-local memory/ store, and "
            "anything else Claude Code has cached for that workspace. "
            "Claude Code recreates the directory on the next launch. "
            "Destructive: prompts for confirmation by default; pass "
            "--force to skip the prompt."
        ),
        epilog=(
            "Examples:\n"
            "  reset-cc-project.py ~/work/eclass-mcp-server\n"
            "  reset-cc-project.py ~/work/eclass-mcp-server --force"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "workspace",
        type=Path,
        help="Absolute path to the workspace directory Claude Code was launched in.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete without the interactive confirmation prompt.",
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
        project_dir = resolve_project_dir(args.workspace, args.project_dir)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    files, subdirs = inventory_project_dir(project_dir)
    if not files and not subdirs:
        print(f"Project directory {project_dir} is already empty; removing it anyway.")
    else:
        print(f"About to remove the entire project directory at {project_dir}:")
        for path in files:
            print(f"  file  {path.name}")
        for path in subdirs:
            print(f"  dir   {path.name}/")
    if not args.force and not confirm("Proceed?"):
        print("Aborted; nothing was deleted.")
        return 2
    if not delete_project_dir(project_dir):
        return 1
    print(f"Done: removed {project_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
