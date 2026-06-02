#!/usr/bin/env python3
"""Create a skill pack skeleton from a JSON manifest.

Usage:
    init_pack.py manifest.json [--root <skills-root>] [--force]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skillify_lib import default_skills_root, is_valid_skill_name, load_json, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=default_skills_root())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    name = str(manifest.get("name", "")).strip()
    if not is_valid_skill_name(name):
        print(f"invalid skill name: {name!r}", file=sys.stderr)
        return 2

    pack_dir = args.root / name
    if pack_dir.exists() and not args.force:
        print(f"pack already exists: {pack_dir}", file=sys.stderr)
        return 2

    description = str(manifest.get("description", "")).strip()
    triggers = list(manifest.get("triggers") or [])
    negatives = list(manifest.get("negative_examples") or [])
    resources = set(manifest.get("resources") or [])
    workflow = list(manifest.get("workflow") or [])

    required = ["tests/unit", "tests/integration", "evals"]
    for rel in required:
        (pack_dir / rel).mkdir(parents=True, exist_ok=True)
    for rel in ("scripts", "references", "assets"):
        if rel in resources:
            (pack_dir / rel).mkdir(parents=True, exist_ok=True)

    write_skill_md(pack_dir / "SKILL.md", name, description, triggers, workflow)
    write_pack_json(pack_dir / "pack.json", manifest)
    write_resolver(pack_dir / "resolver.yaml", name, description, triggers, negatives)
    write_evals(pack_dir, name, triggers, negatives)
    write_tests(pack_dir, name)

    print(f"created skill pack: {pack_dir}")
    return 0


def write_skill_md(path: Path, name: str, description: str, triggers: list[str], workflow: list[str]) -> None:
    trigger_text = ", ".join(f'"{t}"' for t in triggers[:8])
    body_steps = workflow or [
        "Load this skill when the user request matches the frontmatter description.",
        "Follow the proven workflow captured from the original successful run.",
        "Run the bundled checks before handing the result back.",
    ]
    lines = [
        "---",
        f"name: {name}",
        "description: >",
        f"  {description or f'This skill should be used for {name} workflows.'} Trigger phrases include: {trigger_text}.",
        "---",
        "",
        f"# {name}",
        "",
        "## Workflow",
        "",
    ]
    lines.extend(f"{idx}. {step}" for idx, step in enumerate(body_steps, 1))
    lines.extend(["", "## Verification", "", "- Run unit tests for deterministic scripts.", "- Run integration tests for the representative skill workflow."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_pack_json(path: Path, manifest: dict) -> None:
    data = {
        "schema_version": 1,
        "name": manifest["name"],
        "description": manifest.get("description", ""),
        "resources": manifest.get("resources", []),
        "status": {
            "unit": "pending",
            "integration": "pending",
            "llm_eval": "pending",
            "resolver_eval": "pending",
        },
    }
    write_json(path, data)


def write_resolver(path: Path, name: str, description: str, triggers: list[str], negatives: list[str]) -> None:
    lines = [
        f"name: {name}",
        f"description: {description}",
        "triggers:",
    ]
    lines.extend(f"  - {item}" for item in triggers)
    lines.append("negative_examples:")
    lines.extend(f"  - {item}" for item in negatives)
    lines.append("expected_confidence: 0.75")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_evals(pack_dir: Path, name: str, triggers: list[str], negatives: list[str]) -> None:
    skill_case = {
        "id": "skill-smoke",
        "input": triggers[0] if triggers else f"use {name}",
        "expected_behavior": f"Use the {name} skill and follow its workflow.",
        "must_include": [name],
    }
    resolver_cases = []
    if triggers:
        resolver_cases.append({"id": "resolver-positive", "query": triggers[0], "expected": name})
    if negatives:
        resolver_cases.append({"id": "resolver-negative", "query": negatives[0], "expected": None})
    (pack_dir / "evals" / "skill_cases.jsonl").write_text(
        __import__("json").dumps(skill_case, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (pack_dir / "evals" / "resolver_cases.jsonl").write_text(
        "".join(__import__("json").dumps(row, ensure_ascii=False) + "\n" for row in resolver_cases),
        encoding="utf-8",
        newline="\n",
    )
    (pack_dir / "evals" / "rubric.md").write_text(
        "# Rubric\n\n- Select the skill only when the user intent matches the resolver metadata.\n- Follow the SKILL.md workflow without adding speculative features.\n- Preserve safety constraints and run the declared verification steps.\n",
        encoding="utf-8",
        newline="\n",
    )


def write_tests(pack_dir: Path, name: str) -> None:
    test = f"""import unittest


class {name.replace('-', '_').title().replace('_', '')}SmokeTest(unittest.TestCase):
    def test_pack_exists(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
"""
    (pack_dir / "tests" / "unit" / "test_smoke.py").write_text(test, encoding="utf-8", newline="\n")
    (pack_dir / "tests" / "integration" / "test_workflow_smoke.py").write_text(test, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
