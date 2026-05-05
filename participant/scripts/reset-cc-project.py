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

This action is destructive. By default it inventories the directory's
contents and prompts for confirmation. Pass ``--force`` to skip the
prompt; the inventory still prints so the action stays observable.

Exit codes: ``0`` on a successful deletion or a confirmed no-op; ``1``
on input errors; ``2`` when the user declines the prompt.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"


def encode_workspace(workspace: Path) -> str:
    """Encode an absolute workspace path the way Claude Code names project directories.

    Args:
        workspace: Resolved absolute workspace path.

    Returns:
        The encoded directory name (each ``/`` becomes ``-``).
    """
    return str(workspace).replace("/", "-")


def resolve_project_dir(workspace: Path) -> Path:
    """Resolve a workspace path to its Claude Code project directory.

    Args:
        workspace: Workspace path supplied by the participant.

    Returns:
        Absolute path to ``~/.claude/projects/<encoded>``.

    Raises:
        FileNotFoundError: If the workspace path does not exist or the
            corresponding project directory does not exist.
    """
    if not workspace.exists():
        raise FileNotFoundError(f"workspace path does not exist: {workspace}")
    if not workspace.is_dir():
        raise FileNotFoundError(f"workspace path is not a directory: {workspace}")
    encoded = encode_workspace(workspace.resolve())
    project_dir = PROJECTS_ROOT / encoded
    if not project_dir.exists():
        raise FileNotFoundError(
            f"no Claude Code project directory found at {project_dir}; "
            f"has Claude Code been launched in {workspace}?"
        )
    return project_dir


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
        project_dir = resolve_project_dir(args.workspace)
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
