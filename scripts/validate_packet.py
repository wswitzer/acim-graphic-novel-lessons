#!/usr/bin/env python3
"""Deterministic structural validator for ACIM daily packet outputs.

This script intentionally validates mechanical requirements only. It cannot prove
spiritual/story quality, but it catches missing required fields, wrong lesson
metadata, missing panel scripts, missing text ownership metadata, and missing
first-panel lesson title cards.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    print("FAIL: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(2) from exc

ALLOWED_TEXT_TYPES = {"caption", "dialogue", "inner_thought", "no_text"}
ALLOWED_RENDER_AS = {"caption_box", "speech_bubble", "thought_bubble"}
REQUIRED_DIGEST_KEYS = [
    "lesson_text_source_used",
    "lesson_core_movement",
    "lesson_practice_shape",
    "key_ideas_for_story",
    "useful_short_phrases",
    "title_overfit_warning",
]
REQUIRED_SELECTION_KEYS = [
    "style_id",
    "style_name",
    "character_id",
    "character_name",
    "story_mode",
    "arc_temperature",
    "arc_stage_used",
    "character_selection_rationale",
    "character_arc_status",
    "recent_same_character_count",
    "lesson_fit_reason",
]
REQUIRED_CONTINUITY_KEYS = [
    "character_memory_used",
    "before_state",
    "inner_movement",
    "miracle_shift",
    "unresolved_thread",
    "updated_memory_proposal",
]


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def get_required(mapping: dict[str, Any], key: str, errors: list[str], context: str) -> Any:
    if key not in mapping or mapping[key] in (None, ""):
        fail(errors, f"{context}: missing required key `{key}`")
        return None
    return mapping[key]


def validate_text_items(panel: dict[str, Any], panel_path: str, errors: list[str]) -> None:
    legacy_text_fields = [k for k in ("caption", "dialogue", "inner_thought") if panel.get(k)]
    text_items = panel.get("text_items")

    if legacy_text_fields and not isinstance(text_items, list):
        fail(errors, f"{panel_path}: has text fields {legacy_text_fields} but no text_items list")
        return

    if text_items is None:
        return

    if not isinstance(text_items, list) or not text_items:
        fail(errors, f"{panel_path}: text_items must be a non-empty list when present")
        return

    for idx, item in enumerate(text_items, start=1):
        item_path = f"{panel_path}.text_items[{idx}]"
        if not isinstance(item, dict):
            fail(errors, f"{item_path}: must be a mapping")
            continue

        for key in ["text_type", "speaker", "text", "render_as", "placement", "tail_anchor"]:
            if key not in item:
                fail(errors, f"{item_path}: missing `{key}`")

        text_type = item.get("text_type")
        render_as = item.get("render_as")
        speaker = item.get("speaker")
        text = item.get("text")
        tail_anchor = item.get("tail_anchor")
        placement = item.get("placement")

        if text_type not in ALLOWED_TEXT_TYPES:
            fail(errors, f"{item_path}: invalid text_type `{text_type}`")
        if render_as not in ALLOWED_RENDER_AS:
            fail(errors, f"{item_path}: invalid render_as `{render_as}`")
        if text_type != "no_text" and not text:
            fail(errors, f"{item_path}: text is required unless text_type is no_text")
        if text_type == "caption":
            if speaker != "Narrator":
                fail(errors, f"{item_path}: caption speaker must be Narrator")
            if render_as != "caption_box":
                fail(errors, f"{item_path}: caption render_as must be caption_box")
            if tail_anchor is not None:
                fail(errors, f"{item_path}: caption tail_anchor must be null")
        if text_type == "dialogue":
            if render_as != "speech_bubble":
                fail(errors, f"{item_path}: dialogue render_as must be speech_bubble")
            if not speaker or speaker == "Narrator":
                fail(errors, f"{item_path}: dialogue speaker must be a character name")
            if not tail_anchor:
                fail(errors, f"{item_path}: dialogue tail_anchor must point to the speaking character")
        if text_type == "inner_thought":
            if render_as != "thought_bubble":
                fail(errors, f"{item_path}: inner_thought render_as must be thought_bubble")
            if not speaker or speaker == "Narrator":
                fail(errors, f"{item_path}: inner_thought speaker must be a character name")
            if not tail_anchor:
                fail(errors, f"{item_path}: inner_thought tail_anchor must point to the thinking character")
        if text_type == "no_text":
            if text not in (None, ""):
                fail(errors, f"{item_path}: no_text entries should not contain renderable text")
        if not placement:
            fail(errors, f"{item_path}: placement must be concrete and non-empty")


def validate_packet(repo_root: Path, lesson_number: int) -> list[str]:
    errors: list[str] = []
    lesson_slug = f"lesson-{lesson_number:03d}"
    packet_path = repo_root / "content" / "packets" / f"{lesson_slug}.yaml"
    daily_path = repo_root / "content" / "daily" / f"{lesson_slug}.md"
    lesson_json_path = repo_root / "data" / "lessons" / f"{lesson_slug}.json"
    log_path = repo_root / "data" / "lesson-log.yaml"
    story_index_path = repo_root / "data" / "story-index.yaml"
    memory_path = repo_root / "data" / "character-memory.yaml"

    for required_path in [packet_path, daily_path, lesson_json_path, log_path, story_index_path, memory_path]:
        if not required_path.exists():
            fail(errors, f"missing required file: {required_path.relative_to(repo_root)}")
    if errors:
        return errors

    try:
        packet = load_yaml(packet_path)
        lesson_json = load_json(lesson_json_path)
        log = load_yaml(log_path)
        story_index = load_yaml(story_index_path)
        memory = load_yaml(memory_path)
    except Exception as exc:
        return [f"failed to parse validation input: {exc}"]

    if not isinstance(packet, dict):
        return ["packet YAML root must be a mapping"]

    expected_title = lesson_json.get("title_clean")
    expected_source = f"data/lessons/{lesson_slug}.json"
    title_card_text = f"Lesson {lesson_number} — {expected_title}\n{packet.get('selection', {}).get('character_name', '')}"

    if packet.get("status") != "draft":
        fail(errors, "packet.status must be draft")

    lesson = get_required(packet, "lesson", errors, "packet") or {}
    if isinstance(lesson, dict):
        if lesson.get("number") != lesson_number:
            fail(errors, f"lesson.number must be {lesson_number}")
        if lesson.get("title") != expected_title:
            fail(errors, "lesson.title must match compact lesson JSON title_clean")
        if lesson.get("source_url") != expected_source:
            fail(errors, f"lesson.source_url must be {expected_source}")

    selection = get_required(packet, "selection", errors, "packet") or {}
    if isinstance(selection, dict):
        for key in REQUIRED_SELECTION_KEYS:
            get_required(selection, key, errors, "selection")
        if selection.get("character_arc_status") not in {"continuing_arc", "new_arc_start", "returning_arc"}:
            fail(errors, "selection.character_arc_status must be continuing_arc, new_arc_start, or returning_arc")
        if "character_reference_filename" in selection:
            expected_ref = f"{str(selection.get('character_name', '')).split()[0]}_ACIM_reference.png"
            if selection.get("character_reference_filename") != expected_ref:
                fail(errors, f"selection.character_reference_filename should be {expected_ref}")

    digest = get_required(packet, "lesson_digest", errors, "packet") or {}
    if isinstance(digest, dict):
        for key in REQUIRED_DIGEST_KEYS:
            get_required(digest, key, errors, "lesson_digest")
        if digest.get("lesson_text_source_used") != expected_source:
            fail(errors, f"lesson_digest.lesson_text_source_used must be {expected_source}")
        key_ideas = digest.get("key_ideas_for_story") or []
        if not isinstance(key_ideas, list) or not (3 <= len(key_ideas) <= 5):
            fail(errors, "lesson_digest.key_ideas_for_story must contain 3-5 items")
        useful = digest.get("useful_short_phrases") or []
        if not isinstance(useful, list) or len(useful) > 3:
            fail(errors, "lesson_digest.useful_short_phrases must contain 0-3 items")

    story = get_required(packet, "story", errors, "packet") or {}
    if isinstance(story, dict):
        for key in ["title", "original_theme", "synopsis"]:
            get_required(story, key, errors, "story")

    continuity = get_required(packet, "continuity", errors, "packet") or {}
    if isinstance(continuity, dict):
        for key in REQUIRED_CONTINUITY_KEYS:
            get_required(continuity, key, errors, "continuity")

    graphic = get_required(packet, "graphic_novel", errors, "packet") or {}
    pages = graphic.get("pages") if isinstance(graphic, dict) else None
    if not isinstance(pages, list) or len(pages) != 4:
        fail(errors, "graphic_novel.pages must contain exactly 4 pages")
    else:
        for page_idx, page in enumerate(pages, start=1):
            page_path = f"graphic_novel.pages[{page_idx}]"
            if not isinstance(page, dict):
                fail(errors, f"{page_path}: page must be a mapping")
                continue
            get_required(page, "title", errors, page_path)
            panels = page.get("panels")
            if not isinstance(panels, list) or len(panels) != 3:
                fail(errors, f"{page_path}: must contain exactly 3 panels")
                continue
            for panel_idx, panel in enumerate(panels, start=1):
                panel_path = f"{page_path}.panels[{panel_idx}]"
                if not isinstance(panel, dict):
                    fail(errors, f"{panel_path}: panel must be a mapping")
                    continue
                visual = panel.get("visual")
                if not isinstance(visual, str) or len(visual.strip()) < 40:
                    fail(errors, f"{panel_path}: visual must be concrete and non-empty")
                has_story_text = any(panel.get(k) for k in ("caption", "dialogue", "inner_thought"))
                if has_story_text and "text_items" not in panel:
                    fail(errors, f"{panel_path}: story text requires text_items")
                validate_text_items(panel, panel_path, errors)

    try:
        first_panel = packet["graphic_novel"]["pages"][0]["panels"][0]
        first_text_items = first_panel.get("text_items", [])
        matching_cards = [
            item for item in first_text_items
            if item.get("text_type") == "caption"
            and item.get("speaker") == "Narrator"
            and item.get("text") == title_card_text
            and item.get("render_as") == "caption_box"
            and item.get("tail_anchor") is None
        ]
        if not matching_cards:
            fail(errors, f"page 1 panel 1 must include exact title card text: {title_card_text!r}")
        visual = first_panel.get("visual", "")
        if "title" not in visual.lower() and "plaque" not in visual.lower() and "caption" not in visual.lower() and "card" not in visual.lower():
            fail(errors, "page 1 panel 1 visual must explicitly describe the title card/plaque/caption")
    except Exception as exc:
        fail(errors, f"could not validate first-panel title card: {exc}")

    prompts = get_required(packet, "image_prompts", errors, "packet") or {}
    if isinstance(prompts, dict):
        for key in ["overall", "page_1", "page_2", "page_3", "page_4"]:
            get_required(prompts, key, errors, "image_prompts")
        page_1_prompt = str(prompts.get("page_1", "")).lower()
        if "title" not in page_1_prompt or "card" not in page_1_prompt:
            fail(errors, "image_prompts.page_1 must mention the title card")

    spanish = get_required(packet, "spanish_practice", errors, "packet") or {}
    if isinstance(spanish, dict):
        get_required(spanish, "phrases", errors, "spanish_practice")
    get_required(packet, "suno_prompt", errors, "packet")

    # Supporting files contain target lesson entries.
    if isinstance(log, dict):
        log_entries = log.get("lessons", [])
        if not any(e.get("lesson_number") == lesson_number for e in log_entries if isinstance(e, dict)):
            fail(errors, "data/lesson-log.yaml is missing target lesson entry")
    if isinstance(story_index, dict):
        story_entries = story_index.get("stories", [])
        if not any(e.get("lesson_number") == lesson_number for e in story_entries if isinstance(e, dict)):
            fail(errors, "data/story-index.yaml is missing target lesson entry")
    if isinstance(memory, dict) and isinstance(selection, dict):
        characters = memory.get("characters", {})
        if selection.get("character_id") not in characters:
            fail(errors, "data/character-memory.yaml is missing selected character entry")

    daily_text = daily_path.read_text(encoding="utf-8")
    if title_card_text not in daily_text:
        fail(errors, "daily markdown must include the exact first-panel title card text")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an ACIM graphic novel packet structurally.")
    parser.add_argument("--lesson", type=int, required=True, help="Lesson number, e.g. 185")
    parser.add_argument("--repo-root", default=".", help="Path to the repository root or validation workspace")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    errors = validate_packet(repo_root, args.lesson)
    if errors:
        print(f"FAIL validate_packet lesson-{args.lesson:03d}: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS validate_packet lesson-{args.lesson:03d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
