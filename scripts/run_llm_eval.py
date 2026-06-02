#!/usr/bin/env python3
"""Validate skill eval fixtures offline.

This is intentionally provider-neutral. A future provider can consume the same
JSONL cases and rubric after this offline shape check passes.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skillify_lib import read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    args = parser.parse_args()
    errors = validate_eval(args.pack_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: offline eval fixtures valid for {args.pack_dir}")
    return 0


def validate_eval(pack_dir: Path) -> list[str]:
    errors: list[str] = []
    eval_dir = pack_dir / "evals"
    rubric = eval_dir / "rubric.md"
    skill_cases = eval_dir / "skill_cases.jsonl"
    resolver_cases = eval_dir / "resolver_cases.jsonl"
    if not rubric.exists() or not rubric.read_text(encoding="utf-8").strip():
        errors.append("missing non-empty evals/rubric.md")
    for path, required in (
        (skill_cases, ("id", "input", "expected_behavior")),
        (resolver_cases, ("id", "query", "expected")),
    ):
        if not path.exists():
            errors.append(f"missing {path}")
            continue
        try:
            rows = read_jsonl(path)
        except Exception as exc:
            errors.append(str(exc))
            continue
        if not rows:
            errors.append(f"{path} must contain at least one case")
        for idx, row in enumerate(rows, 1):
            for key in required:
                if key not in row:
                    errors.append(f"{path}:{idx}: missing {key}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
