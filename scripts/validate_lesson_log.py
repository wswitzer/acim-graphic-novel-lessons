#!/usr/bin/env python3
"""Deterministic validator for packet and page-image lifecycle metadata."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    print("FAIL: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2) from exc

OVERALL_IMAGE_STATUSES = {"not_started", "in_progress", "partial", "complete", "failed"}
PAGE_IMAGE_STATUSES = {"not_started", "in_progress", "complete", "failed"}
PACKET_VALIDATION_STATUSES = {"passed", "failed", "not_recorded"}
LEGACY_AMBIGUOUS_FIELDS = {"status", "generated_at_local", "validation_passed", "validation_notes"}


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def expected_page_path(lesson_number: int, page_number: int) -> str:
    return f"assets/images/lesson-{lesson_number:03d}/page-{page_number}.png"


def validate_log_entry(
    entry: dict[str, Any],
    lesson_number: int,
    packet: dict[str, Any] | None = None,
    expect_page_images: str = "any",
) -> list[str]:
    errors: list[str] = []
    context = f"lesson-log lesson-{lesson_number:03d}"

    for field in LEGACY_AMBIGUOUS_FIELDS:
        if field in entry:
            errors.append(f"{context}: legacy ambiguous field `{field}` must not be present")

    if entry.get("lesson_number") != lesson_number:
        errors.append(f"{context}: lesson_number must be {lesson_number}")

    expected_packet_path = f"content/packets/lesson-{lesson_number:03d}.yaml"
    expected_daily_path = f"content/daily/lesson-{lesson_number:03d}.md"
    if entry.get("packet_path") != expected_packet_path:
        errors.append(f"{context}: packet_path must be {expected_packet_path}")
    if entry.get("daily_path") != expected_daily_path:
        errors.append(f"{context}: daily_path must be {expected_daily_path}")

    if entry.get("packet_status") != "complete":
        errors.append(f"{context}: packet_status must be complete")
    if not entry.get("packet_generated_at_local"):
        errors.append(f"{context}: packet_generated_at_local must be a concrete timestamp")
    if entry.get("packet_validation_status") not in PACKET_VALIDATION_STATUSES:
        errors.append(
            f"{context}: packet_validation_status must be one of {sorted(PACKET_VALIDATION_STATUSES)}"
        )
    if entry.get("packet_validation_status") != "passed":
        errors.append(f"{context}: new packet output must have packet_validation_status: passed")
    if not entry.get("packet_validation_notes"):
        errors.append(f"{context}: packet_validation_notes must be non-empty")

    if packet is not None:
        selection = packet.get("selection", {}) if isinstance(packet, dict) else {}
        if entry.get("date") != packet.get("target_date"):
            errors.append(f"{context}: date must match packet.target_date")
        comparisons = {
            "style_id": selection.get("style_id"),
            "character_id": selection.get("character_id"),
            "story_mode": selection.get("story_mode"),
            "arc_temperature": selection.get("arc_temperature"),
        }
        for field, expected in comparisons.items():
            if entry.get(field) != expected:
                errors.append(f"{context}: {field} must match packet.selection.{field}")

    images = entry.get("page_images")
    if not isinstance(images, dict):
        return errors + [f"{context}: page_images must be a mapping"]

    overall_status = images.get("status")
    if overall_status not in OVERALL_IMAGE_STATUSES:
        errors.append(f"{context}: invalid page_images.status `{overall_status}`")
    if expect_page_images != "any" and overall_status != expect_page_images:
        errors.append(
            f"{context}: page_images.status must be {expect_page_images} for this validation run"
        )

    if images.get("expected_count") != 4:
        errors.append(f"{context}: page_images.expected_count must be 4")

    pages = images.get("pages")
    if not isinstance(pages, list) or len(pages) != 4:
        return errors + [f"{context}: page_images.pages must contain exactly 4 pages"]

    seen_numbers: set[int] = set()
    complete_count = 0
    page_statuses: list[str] = []
    for page in pages:
        if not isinstance(page, dict):
            errors.append(f"{context}: each page_images.pages item must be a mapping")
            continue
        page_number = page.get("page_number")
        if page_number not in {1, 2, 3, 4}:
            errors.append(f"{context}: page_number must be 1, 2, 3, or 4")
            continue
        if page_number in seen_numbers:
            errors.append(f"{context}: duplicate page_number {page_number}")
        seen_numbers.add(page_number)

        status = page.get("status")
        page_statuses.append(status)
        if status not in PAGE_IMAGE_STATUSES:
            errors.append(f"{context}: page {page_number} has invalid status `{status}`")
        if page.get("path") != expected_page_path(lesson_number, page_number):
            errors.append(
                f"{context}: page {page_number} path must be {expected_page_path(lesson_number, page_number)}"
            )
        generated_at = page.get("generated_at_local")
        if status == "complete":
            complete_count += 1
            if not generated_at:
                errors.append(f"{context}: complete page {page_number} needs generated_at_local")
        elif generated_at is not None:
            errors.append(
                f"{context}: non-complete page {page_number} must have generated_at_local: null"
            )

    if seen_numbers != {1, 2, 3, 4}:
        errors.append(f"{context}: page_images.pages must contain page numbers 1 through 4 exactly once")

    if images.get("generated_count") != complete_count:
        errors.append(
            f"{context}: generated_count must equal complete page count ({complete_count})"
        )

    completed_at = images.get("completed_at_local")
    if overall_status == "complete":
        if complete_count != 4:
            errors.append(f"{context}: complete status requires all 4 pages complete")
        if not completed_at:
            errors.append(f"{context}: complete status requires completed_at_local")
    else:
        if completed_at is not None:
            errors.append(f"{context}: completed_at_local must be null unless status is complete")

    if overall_status == "not_started":
        if complete_count != 0 or any(status != "not_started" for status in page_statuses):
            errors.append(f"{context}: not_started requires all page statuses to be not_started")
    elif overall_status == "in_progress":
        if "in_progress" not in page_statuses or complete_count == 4:
            errors.append(f"{context}: in_progress requires at least one in_progress page")
    elif overall_status == "partial":
        if not (1 <= complete_count <= 3) or "in_progress" in page_statuses:
            errors.append(
                f"{context}: partial requires 1-3 complete pages and no in_progress pages"
            )
    elif overall_status == "failed":
        if complete_count != 0 or not images.get("last_error"):
            errors.append(
                f"{context}: failed requires zero complete pages and a non-empty last_error"
            )

    return errors


def validate_repository(repo_root: Path, lesson_number: int, expect_page_images: str) -> list[str]:
    log_path = repo_root / "data" / "lesson-log.yaml"
    packet_path = repo_root / "content" / "packets" / f"lesson-{lesson_number:03d}.yaml"
    missing = [path for path in (log_path, packet_path) if not path.exists()]
    if missing:
        return [f"missing required file: {path.relative_to(repo_root)}" for path in missing]

    try:
        log = load_yaml(log_path)
        packet = load_yaml(packet_path)
    except Exception as exc:
        return [f"failed to parse lifecycle validation input: {exc}"]

    entries = log.get("lessons", []) if isinstance(log, dict) else []
    matches = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("lesson_number") == lesson_number
    ]
    if len(matches) != 1:
        return [
            f"data/lesson-log.yaml must contain exactly one entry for lesson {lesson_number}; found {len(matches)}"
        ]

    return validate_log_entry(matches[0], lesson_number, packet, expect_page_images)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate ACIM packet and page-image lifecycle metadata."
    )
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--expect-page-images",
        choices=["any", *sorted(OVERALL_IMAGE_STATUSES)],
        default="any",
    )
    args = parser.parse_args()

    errors = validate_repository(
        Path(args.repo_root).resolve(), args.lesson, args.expect_page_images
    )
    if errors:
        print(f"FAIL validate_lesson_log lesson-{args.lesson:03d}: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS validate_lesson_log lesson-{args.lesson:03d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
