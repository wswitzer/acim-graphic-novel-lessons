import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_lesson_log.py"
spec = importlib.util.spec_from_file_location("validate_lesson_log", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def make_entry(status="not_started", complete_pages=0):
    pages = []
    for page_number in range(1, 5):
        complete = page_number <= complete_pages
        pages.append(
            {
                "page_number": page_number,
                "status": "complete" if complete else "not_started",
                "path": f"assets/images/lesson-189/page-{page_number}.png",
                "generated_at_local": "2026-07-09T22:10:00-06:00" if complete else None,
            }
        )
    return {
        "lesson_number": 189,
        "date": "2026-07-08",
        "style_id": "STYLE-009",
        "character_id": "CHAR-001",
        "story_mode": "integration",
        "arc_temperature": 2,
        "packet_path": "content/packets/lesson-189.yaml",
        "daily_path": "content/daily/lesson-189.md",
        "packet_status": "complete",
        "packet_generated_at_local": "2026-07-09T22:05:00-06:00",
        "packet_validation_status": "passed",
        "packet_validation_notes": "Both deterministic validators passed.",
        "page_images": {
            "status": status,
            "expected_count": 4,
            "generated_count": complete_pages,
            "completed_at_local": "2026-07-09T22:10:00-06:00" if status == "complete" else None,
            "pages": pages,
        },
    }


PACKET = {
    "target_date": "2026-07-08",
    "selection": {
        "style_id": "STYLE-009",
        "character_id": "CHAR-001",
        "story_mode": "integration",
        "arc_temperature": 2,
    },
}


class LessonLogValidationTests(unittest.TestCase):
    def test_new_packet_initializes_images_as_not_started(self):
        errors = module.validate_log_entry(
            make_entry(), 189, PACKET, expect_page_images="not_started"
        )
        self.assertEqual(errors, [])

    def test_generated_count_must_match_complete_pages(self):
        entry = make_entry(status="partial", complete_pages=2)
        entry["page_images"]["generated_count"] = 1
        errors = module.validate_log_entry(entry, 189, PACKET)
        self.assertTrue(any("generated_count" in error for error in errors))

    def test_complete_requires_all_four_pages_and_completion_timestamp(self):
        entry = make_entry(status="complete", complete_pages=3)
        entry["page_images"]["completed_at_local"] = None
        errors = module.validate_log_entry(entry, 189, PACKET)
        self.assertTrue(any("all 4 pages" in error for error in errors))
        self.assertTrue(any("completed_at_local" in error for error in errors))

    def test_legacy_ambiguous_fields_are_rejected(self):
        entry = make_entry()
        entry["status"] = "draft"
        entry["validation_passed"] = True
        errors = module.validate_log_entry(entry, 189, PACKET)
        self.assertTrue(any("legacy ambiguous field `status`" in error for error in errors))
        self.assertTrue(any("legacy ambiguous field `validation_passed`" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
