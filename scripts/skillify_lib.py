#!/usr/bin/env python3
"""Shared helpers for skillify scripts."""
from __future__ import annotations

import json
import re
from pathlib import Path

SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def skillify_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_skills_root() -> Path:
    return skillify_dir().parent


def is_valid_skill_name(name: str) -> bool:
    return bool(SKILL_NAME_RE.fullmatch(name or ""))


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
    return rows


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    raw = text[4:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    return parse_simple_yaml(raw), body


def parse_simple_yaml(text: str) -> dict:
    """Parse the small YAML subset used by skillify metadata.

    Supports top-level scalar keys, folded block scalars (`>` or `|`), and
    top-level lists written as indented `- value` items.
    """
    result: dict[str, object] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"unexpected indentation: {line!r}")
        if ":" not in line:
            raise ValueError(f"expected key:value line: {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise ValueError("empty YAML key")
        if value in (">", "|"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            result[key] = (" " if value == ">" else "\n").join(x for x in block if x)
            continue
        if value == "":
            items = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or not lines[i].strip()):
                child = lines[i].strip()
                if child:
                    if not child.startswith("- "):
                        raise ValueError(f"expected list item under {key}: {lines[i]!r}")
                    items.append(unquote(child[2:].strip()))
                i += 1
            result[key] = items
            continue
        result[key] = unquote(value)
        i += 1
    return result


def unquote(value: str) -> object:
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def load_resolver(path: Path) -> dict:
    data = parse_simple_yaml(path.read_text(encoding="utf-8"))
    data.setdefault("triggers", [])
    data.setdefault("negative_examples", [])
    data.setdefault("expected_confidence", 0.65)
    return data


def registry_path() -> Path:
    return skillify_dir() / "registry.json"
