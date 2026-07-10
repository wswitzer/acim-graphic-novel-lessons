#!/usr/bin/env python3
"""Synchronize page-image lifecycle metadata from exact files on disk."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import yaml  # type: ignore

LOCAL_TIMEZONE = ZoneInfo("America/Mexico_City")


def expected_page_path(lesson_number: int, page_number: int) -> str:
    return f"assets/images/lesson-{lesson_number:03d}/page-{page_number}.png"


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=LOCAL_TIMEZONE).isoformat(timespec="seconds")


def sync_entry(entry: dict[str, Any], repo_root: Path) -> bool:
    lesson_number = entry.get("lesson_number")
    if not isinstance(lesson_number, int):
        raise ValueError("Every lesson-log entry must have an integer lesson_number")

    existing_images = entry.get("page_images") if isinstance(entry.get("page_images"), dict) else {}
    existing_pages = {
        page.get("page_number"): page
        for page in existing_images.get("pages", [])
        if isinstance(page, dict) and page.get("page_number") in {1, 2, 3, 4}
    }

    pages: list[dict[str, Any]] = []
    completed_timestamps: list[str] = []
    for page_number in range(1, 5):
        relative_path = expected_page_path(lesson_number, page_number)
        absolute_path = repo_root / relative_path
        existing_page = existing_pages.get(page_number, {})
        if absolute_path.is_file():
            timestamp = existing_page.get("generated_at_local") or file_timestamp(absolute_path)
            status = "complete"
            completed_timestamps.append(timestamp)
        else:
            timestamp = None
            status = "not_started"
        pages.append(
            {
                "page_number": page_number,
                "status": status,
                "path": relative_path,
                "generated_at_local": timestamp,
            }
        )

    generated_count = len(completed_timestamps)
    if generated_count == 4:
        overall_status = "complete"
        completed_at = max(completed_timestamps)
    elif generated_count > 0:
        overall_status = "partial"
        completed_at = None
    else:
        overall_status = "not_started"
        completed_at = None

    new_images = {
        "status": overall_status,
        "expected_count": 4,
        "generated_count": generated_count,
        "completed_at_local": completed_at,
        "pages": pages,
    }
    changed = entry.get("page_images") != new_images
    entry["page_images"] = new_images
    return changed


def sync_log(repo_root: Path, lesson_number: int | None = None) -> tuple[int, bool]:
    log_path = repo_root / "data" / "lesson-log.yaml"
    with log_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict) or not isinstance(data.get("lessons"), list):
        raise ValueError("data/lesson-log.yaml must contain a lessons list")

    matched = 0
    changed = False
    for entry in data["lessons"]:
        if not isinstance(entry, dict):
            continue
        if lesson_number is not None and entry.get("lesson_number") != lesson_number:
            continue
        matched += 1
        changed = sync_entry(entry, repo_root) or changed

    if lesson_number is not None and matched != 1:
        raise ValueError(
            f"Expected exactly one lesson-log entry for lesson {lesson_number}; found {matched}"
        )

    if changed:
        with log_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True, width=110)

    return matched, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    matched, changed = sync_log(Path(args.repo_root).resolve(), args.lesson)
    scope = f"lesson-{args.lesson:03d}" if args.lesson is not None else f"{matched} lessons"
    print(f"SYNC lesson-log page images: {scope}; changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
