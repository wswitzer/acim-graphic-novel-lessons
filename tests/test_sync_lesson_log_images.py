import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sync_lesson_log_images.py"
spec = importlib.util.spec_from_file_location("sync_lesson_log_images", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class SyncLessonLogImagesTests(unittest.TestCase):
    def make_repo(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "data").mkdir(parents=True)
        log = {
            "lessons": [
                {
                    "lesson_number": 189,
                    "page_images": {
                        "status": "not_started",
                        "expected_count": 4,
                        "generated_count": 0,
                        "completed_at_local": None,
                        "pages": [],
                    },
                }
            ]
        }
        (root / "data" / "lesson-log.yaml").write_text(
            yaml.safe_dump(log, sort_keys=False), encoding="utf-8"
        )
        return temp, root

    def read_entry(self, root):
        data = yaml.safe_load((root / "data" / "lesson-log.yaml").read_text(encoding="utf-8"))
        return data["lessons"][0]

    def test_no_files_is_not_started(self):
        temp, root = self.make_repo()
        with temp:
            module.sync_log(root, 189)
            images = self.read_entry(root)["page_images"]
            self.assertEqual(images["status"], "not_started")
            self.assertEqual(images["generated_count"], 0)
            self.assertTrue(all(page["status"] == "not_started" for page in images["pages"]))

    def test_two_files_is_partial(self):
        temp, root = self.make_repo()
        with temp:
            image_dir = root / "assets" / "images" / "lesson-189"
            image_dir.mkdir(parents=True)
            (image_dir / "page-1.png").write_bytes(b"one")
            (image_dir / "page-3.png").write_bytes(b"three")
            module.sync_log(root, 189)
            images = self.read_entry(root)["page_images"]
            self.assertEqual(images["status"], "partial")
            self.assertEqual(images["generated_count"], 2)
            self.assertIsNone(images["completed_at_local"])

    def test_four_files_is_complete(self):
        temp, root = self.make_repo()
        with temp:
            image_dir = root / "assets" / "images" / "lesson-189"
            image_dir.mkdir(parents=True)
            for page_number in range(1, 5):
                (image_dir / f"page-{page_number}.png").write_bytes(b"image")
            module.sync_log(root, 189)
            images = self.read_entry(root)["page_images"]
            self.assertEqual(images["status"], "complete")
            self.assertEqual(images["generated_count"], 4)
            self.assertIsNotNone(images["completed_at_local"])
            self.assertTrue(all(page["status"] == "complete" for page in images["pages"]))


if __name__ == "__main__":
    unittest.main()
