#!/usr/bin/env python3
"""Render the skillify registry into an interactive HTML report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from skillify_lib import registry_path, skillify_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("registry", nargs="?", type=Path, default=registry_path())
    parser.add_argument("output", nargs="?", type=Path, default=skillify_dir() / "skillify-report.html")
    args = parser.parse_args()
    data = json.loads(args.registry.read_text(encoding="utf-8"))
    template = (skillify_dir() / "assets" / "report_template.html").read_text(encoding="utf-8")
    html = template.replace("__REGISTRY_DATA__", json.dumps(data, ensure_ascii=False))
    args.output.write_text(html, encoding="utf-8", newline="\n")
    print(f"report written: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
