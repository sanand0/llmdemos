#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PREFERRED_COLUMNS = [
    "title",
    "url",
    "description",
    "created",
    "license",
    "repo",
    "icon",
    "reviewed",
    "unreviewed",
]


def as_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_columns(demos: list[dict]) -> list[str]:
    keys = {k for demo in demos for k in demo.keys()}
    ordered = [k for k in PREFERRED_COLUMNS if k in keys]
    extras = sorted(keys - set(ordered))
    return ordered + extras


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.json")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("llmdemos.csv")

    payload = json.loads(src.read_text(encoding="utf-8"))
    demos = payload.get("demos", [])
    if not isinstance(demos, list):
        raise SystemExit(f"{src} is missing a list at .demos")

    columns = build_columns(demos)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for demo in demos:
            writer.writerow({col: as_cell(demo.get(col)) for col in columns})

    print(f"Wrote {len(demos)} demos to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
