#!/usr/bin/env python3
"""Resolve selected Git conflict blocks without discarding non-conflicting changes.

The script operates on an already conflicted worktree. For each listed path it
replaces every standard conflict block with either the local (ours) or incoming
(theirs) section. Text outside conflict markers is left unchanged, so clean
upstream hunks already applied by Git are preserved.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

MARKER_RE = re.compile(br"^(<<<<<<<|=======|>>>>>>>)", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--paths-file", type=Path, required=True)
    parser.add_argument("--choice", choices=("ours", "theirs"), required=True)
    return parser.parse_args()


def read_paths(path: Path) -> list[str]:
    entries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        item = raw.strip()
        if not item or item.startswith("#"):
            continue
        if item.startswith("/") or ".." in Path(item).parts:
            raise ValueError(f"unsafe repository path: {item}")
        entries.append(item)
    if len(entries) != len(set(entries)):
        raise ValueError("paths file contains duplicate entries")
    return entries


def resolve_bytes(data: bytes, choice: str, repo_path: str) -> tuple[bytes, int]:
    lines = data.splitlines(keepends=True)
    output: list[bytes] = []
    index = 0
    blocks = 0

    while index < len(lines):
        line = lines[index]
        if not line.startswith(b"<<<<<<<"):
            output.append(line)
            index += 1
            continue

        blocks += 1
        index += 1
        ours: list[bytes] = []
        while index < len(lines) and not lines[index].startswith(b"======="):
            if lines[index].startswith((b"<<<<<<<", b">>>>>>>")):
                raise ValueError(f"nested or malformed conflict in {repo_path}")
            ours.append(lines[index])
            index += 1

        if index >= len(lines):
            raise ValueError(f"missing ======= marker in {repo_path}")
        index += 1

        theirs: list[bytes] = []
        while index < len(lines) and not lines[index].startswith(b">>>>>>>"):
            if lines[index].startswith((b"<<<<<<<", b"=======")):
                raise ValueError(f"nested or malformed conflict in {repo_path}")
            theirs.append(lines[index])
            index += 1

        if index >= len(lines):
            raise ValueError(f"missing >>>>>>> marker in {repo_path}")
        index += 1
        output.extend(ours if choice == "ours" else theirs)

    resolved = b"".join(output)
    if MARKER_RE.search(resolved):
        raise ValueError(f"unresolved conflict marker remains in {repo_path}")
    return resolved, blocks


def atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.resolve-tmp")
    temporary.write_bytes(data)
    os.chmod(temporary, path.stat().st_mode)
    temporary.replace(path)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    paths = read_paths(args.paths_file)
    total_blocks = 0

    for repo_path in paths:
        target = (root / repo_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"path escapes repository root: {repo_path}") from exc
        if not target.is_file():
            raise FileNotFoundError(f"conflicted file not found: {repo_path}")

        resolved, blocks = resolve_bytes(target.read_bytes(), args.choice, repo_path)
        if blocks == 0:
            raise ValueError(f"listed path has no conflict markers: {repo_path}")
        atomic_write(target, resolved)
        total_blocks += blocks
        print(f"resolved {blocks:2d} block(s): {repo_path}")

    print(f"resolved {total_blocks} conflict block(s) across {len(paths)} path(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line diagnostics
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
