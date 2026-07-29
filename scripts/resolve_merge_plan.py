#!/usr/bin/env python3
"""Resolve conflict blocks according to an auditable per-file JSON plan."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--plan", type=Path, required=True)
    return parser.parse_args()


def atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.plan-tmp")
    temporary.write_bytes(data)
    os.chmod(temporary, path.stat().st_mode)
    temporary.replace(path)


def parse_blocks(data: bytes, repo_path: str) -> tuple[list[bytes], list[tuple[list[bytes], list[bytes]]]]:
    lines = data.splitlines(keepends=True)
    segments: list[bytes] = []
    blocks: list[tuple[list[bytes], list[bytes]]] = []
    plain: list[bytes] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.startswith(b"<<<<<<<"):
            plain.append(line)
            index += 1
            continue

        segments.append(b"".join(plain))
        plain = []
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
        blocks.append((ours, theirs))

    segments.append(b"".join(plain))
    return segments, blocks


def replacement(decision: Any, ours: list[bytes], theirs: list[bytes], repo_path: str, block_no: int) -> bytes:
    if decision == "ours":
        return b"".join(ours)
    if decision == "theirs":
        return b"".join(theirs)
    if isinstance(decision, dict) and set(decision) == {"custom"}:
        text = decision["custom"]
        if not isinstance(text, str):
            raise TypeError(f"custom replacement must be text: {repo_path} block {block_no}")
        return text.encode("utf-8")
    raise ValueError(f"invalid decision for {repo_path} block {block_no}: {decision!r}")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or not plan:
        raise ValueError("plan must be a non-empty object")

    total_blocks = 0
    for repo_path, decisions in plan.items():
        if not isinstance(repo_path, str) or repo_path.startswith("/") or ".." in Path(repo_path).parts:
            raise ValueError(f"unsafe repository path: {repo_path!r}")
        if not isinstance(decisions, list):
            raise TypeError(f"decisions must be a list: {repo_path}")

        target = (root / repo_path).resolve()
        target.relative_to(root)
        if not target.is_file():
            raise FileNotFoundError(f"conflicted file not found: {repo_path}")

        segments, blocks = parse_blocks(target.read_bytes(), repo_path)
        if len(blocks) != len(decisions):
            raise ValueError(
                f"block count mismatch for {repo_path}: file has {len(blocks)}, plan has {len(decisions)}"
            )

        output: list[bytes] = [segments[0]]
        for index, ((ours, theirs), decision) in enumerate(zip(blocks, decisions, strict=True), start=1):
            output.append(replacement(decision, ours, theirs, repo_path, index))
            output.append(segments[index])

        resolved = b"".join(output)
        if any(line.startswith((b"<<<<<<<", b"=======", b">>>>>>>")) for line in resolved.splitlines()):
            raise ValueError(f"unresolved marker remains in {repo_path}")
        atomic_write(target, resolved)
        total_blocks += len(blocks)
        print(f"resolved {len(blocks):2d} planned block(s): {repo_path}")

    print(f"resolved {total_blocks} planned conflict block(s) across {len(plan)} file(s)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
