#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

PREFERRED_COLUMNS = [
    "title",
    "url",
    "description",
    "created",
    "license",
    "repo",
    "icon",
    "branded",
    "brands",
    "reviewed",
]


def as_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def build_columns(demos: list[dict[str, Any]]) -> list[str]:
    keys = {k for demo in demos for k in demo.keys()}
    ordered = [k for k in PREFERRED_COLUMNS if k in keys]
    extras = sorted(keys - set(ordered))
    return ordered + extras


def write_csv(dst: Path, demos: list[dict[str, Any]], columns: list[str]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for demo in demos:
            writer.writerow({col: as_cell(demo.get(col)) for col in columns})


def build_open_demos(demos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for demo in demos:
        if not isinstance(demo, dict) or demo.get("reviewed") is not True:
            continue
        repo = demo.get("repo")
        if not repo:
            continue

        created = demo.get("created")
        entry = grouped.setdefault(
            repo,
            {
                "repo": repo,
                "license": "",
                "created": created,
                "title": demo.get("title"),
                "branded": False,
            },
        )
        if demo.get("license") == "MIT":
            entry["license"] = "MIT"
        if demo.get("branded") is True:
            entry["branded"] = True
        if created and (not entry["created"] or created < entry["created"]):
            entry["created"] = created
            entry["title"] = demo.get("title")

    open_demos = [entry for entry in grouped.values() if entry["license"] == "MIT"]
    return sorted(open_demos, key=lambda demo: (demo.get("created") or "", demo["repo"]), reverse=True)


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("config.json")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("llmdemos.csv")
    open_dst = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("open-demos.csv")

    payload = json.loads(src.read_text(encoding="utf-8"))
    demos = payload.get("demos", [])
    if not isinstance(demos, list):
        raise SystemExit(f"{src} is missing a list at .demos")

    columns = build_columns(demos)
    write_csv(dst, demos, columns)

    print(f"Wrote {len(demos)} demos to {dst}")
    open_demos = build_open_demos(demos)
    open_columns = ["repo", "license", "created", "title", "branded"]
    write_csv(open_dst, open_demos, open_columns)
    print(f"Wrote {len(open_demos)} open demos to {open_dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
