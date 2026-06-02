#!/usr/bin/env python3
"""Validate a skill pack structure."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skillify_lib import (
    is_valid_skill_name,
    load_resolver,
    parse_frontmatter,
    read_jsonl,
)

REQUIRED_PATHS = [
    "SKILL.md",
    "pack.json",
    "resolver.yaml",
    "tests/unit",
    "tests/integration",
    "evals/skill_cases.jsonl",
    "evals/resolver_cases.jsonl",
    "evals/rubric.md",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    args = parser.parse_args()
    errors = validate_pack(args.pack_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.pack_dir}")
    return 0


def validate_pack(pack_dir: Path) -> list[str]:
    errors: list[str] = []
    if not pack_dir.exists():
        return [f"missing pack directory: {pack_dir}"]
    for rel in REQUIRED_PATHS:
        if not (pack_dir / rel).exists():
            errors.append(f"missing {rel}")

    skill_md = pack_dir / "SKILL.md"
    if skill_md.exists():
        try:
            fm, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            name = str(fm.get("name", ""))
            description = str(fm.get("description", ""))
            if not is_valid_skill_name(name):
                errors.append(f"invalid frontmatter name: {name!r}")
            if name != pack_dir.name:
                errors.append(f"frontmatter name {name!r} does not match folder {pack_dir.name!r}")
            if not description.strip():
                errors.append("missing frontmatter description")
            if not body.strip():
                errors.append("empty SKILL.md body")
        except Exception as exc:
            errors.append(f"invalid SKILL.md frontmatter: {exc}")

    resolver = pack_dir / "resolver.yaml"
    if resolver.exists():
        try:
            data = load_resolver(resolver)
            if data.get("name") != pack_dir.name:
                errors.append("resolver name does not match folder name")
            if not data.get("triggers"):
                errors.append("resolver.yaml requires at least one trigger")
            confidence = float(data.get("expected_confidence", 0))
            if confidence <= 0 or confidence > 1:
                errors.append("expected_confidence must be between 0 and 1")
        except Exception as exc:
            errors.append(f"invalid resolver.yaml: {exc}")

    for rel in ("evals/skill_cases.jsonl", "evals/resolver_cases.jsonl"):
        path = pack_dir / rel
        if path.exists():
            try:
                read_jsonl(path)
            except Exception as exc:
                errors.append(str(exc))

    rubric = pack_dir / "evals" / "rubric.md"
    if rubric.exists() and not rubric.read_text(encoding="utf-8").strip():
        errors.append("empty evals/rubric.md")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
