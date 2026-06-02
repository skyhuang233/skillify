#!/usr/bin/env python3
"""Resolve the best matching skill for a user query."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from skillify_lib import default_skills_root, load_resolver

WORD_RE = re.compile(r"[a-z0-9\u4e00-\u9fff]+", re.IGNORECASE)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_skills_root())
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    matches = resolve(args.root, args.query, args.limit)
    print(json.dumps({"query": args.query, "matches": matches}, ensure_ascii=False, indent=2))
    return 0


def resolve(root: Path, query: str, limit: int = 5) -> list[dict]:
    matches = []
    for resolver_path in root.glob("*/resolver.yaml"):
        meta = load_resolver(resolver_path)
        score = score_query(query, meta)
        if score <= 0:
            continue
        matches.append(
            {
                "name": meta.get("name") or resolver_path.parent.name,
                "score": round(score, 3),
                "expected_confidence": float(meta.get("expected_confidence", 0.65)),
                "description": meta.get("description", ""),
            }
        )
    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:limit]


def score_query(query: str, meta: dict) -> float:
    q = normalize(query)
    if not q:
        return 0.0
    for negative in meta.get("negative_examples") or []:
        n = normalize(str(negative))
        if n and n in q:
            return 0.0
    best = 0.0
    for trigger in meta.get("triggers") or []:
        t = normalize(str(trigger))
        if not t:
            continue
        if t in q:
            best = max(best, 1.0)
        else:
            best = max(best, token_overlap(q, t) * 0.85)
    description = normalize(str(meta.get("description", "")))
    if description:
        best = max(best, token_overlap(q, description) * 0.45)
    return best


def normalize(text: str) -> str:
    return " ".join(WORD_RE.findall(text.lower()))


def token_overlap(a: str, b: str) -> float:
    aset = set(a.split())
    bset = set(b.split())
    if not aset or not bset:
        return 0.0
    return len(aset & bset) / len(aset)


if __name__ == "__main__":
    raise SystemExit(main())
