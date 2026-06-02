#!/usr/bin/env python3
"""Run unit and integration tests for a skill pack."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack_dir", type=Path)
    args = parser.parse_args()
    pack_dir = args.pack_dir.resolve()
    targets = [pack_dir / "tests" / "unit", pack_dir / "tests" / "integration"]
    failures = 0
    for target in targets:
        if not target.exists():
            print(f"SKIP: {target}")
            continue
        print(f"RUN: {target}")
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(target)],
            cwd=str(pack_dir),
        )
        if result.returncode != 0:
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
