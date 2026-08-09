"""
Tests for the persistent cross-task memory system.

Run with: python -m unittest harness.tests.test_memory -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from harness.memory import MemoryStore, MemoryCategory


class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_memory_test_")
        self.store = MemoryStore(path=str(Path(self.tmp_dir) / "memory.jsonl"))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_remember_and_recall_roundtrip(self):
        self.store.remember(
            category=MemoryCategory.BRAND_PROFILE,
            subject="acme.com",
            content={"primary_color": "#123456", "font": "Helvetica"},
            tags=["ecommerce", "b2c"],
            task_id="task_1",
        )

        results = self.store.recall(subject="acme.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content["primary_color"], "#123456")
        self.assertEqual(results[0].category, MemoryCategory.BRAND_PROFILE)

    def test_recall_filters_by_category(self):
        self.store.remember(MemoryCategory.BRAND_PROFILE, "acme.com", {"a": 1})
        self.store.remember(MemoryCategory.SITE_INSPECTION, "acme.com", {"b": 2})

        brand_only = self.store.recall(subject="acme.com", category=MemoryCategory.BRAND_PROFILE)
        self.assertEqual(len(brand_only), 1)
        self.assertEqual(brand_only[0].content, {"a": 1})

    def test_recall_filters_by_tags(self):
        self.store.remember(MemoryCategory.PROSPECT_SCORE, "site-a.com", {"score": 80}, tags=["hot_lead"])
        self.store.remember(MemoryCategory.PROSPECT_SCORE, "site-b.com", {"score": 20}, tags=["cold_lead"])

        hot = self.store.recall(category=MemoryCategory.PROSPECT_SCORE, tags=["hot_lead"])
        self.assertEqual(len(hot), 1)
        self.assertEqual(hot[0].subject, "site-a.com")

    def test_latest_returns_most_recent_for_subject_and_category(self):
        self.store.remember(MemoryCategory.SITE_INSPECTION, "acme.com", {"version": 1})
        self.store.remember(MemoryCategory.SITE_INSPECTION, "acme.com", {"version": 2})

        latest = self.store.latest("acme.com", MemoryCategory.SITE_INSPECTION)
        self.assertEqual(latest.content["version"], 2)

    def test_latest_returns_none_when_no_memory_exists(self):
        latest = self.store.latest("never-seen.com", MemoryCategory.BRAND_PROFILE)
        self.assertIsNone(latest)

    def test_search_text_matches_subject_tags_and_content(self):
        self.store.remember(
            MemoryCategory.LESSON_LEARNED,
            "acme.com",
            {"note": "client rejected bold typography, prefers minimalist serif"},
            tags=["typography"],
        )
        self.store.remember(MemoryCategory.LESSON_LEARNED, "other.com", {"note": "unrelated"})

        results = self.store.search_text("minimalist")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].subject, "acme.com")

        results_by_tag = self.store.search_text("typography")
        self.assertEqual(len(results_by_tag), 1)

    def test_forget_subject_removes_all_its_memories(self):
        self.store.remember(MemoryCategory.BRAND_PROFILE, "acme.com", {"a": 1})
        self.store.remember(MemoryCategory.SITE_INSPECTION, "acme.com", {"b": 2})
        self.store.remember(MemoryCategory.BRAND_PROFILE, "other.com", {"c": 3})

        removed = self.store.forget_subject("acme.com")
        self.assertEqual(removed, 2)

        self.assertEqual(len(self.store.recall(subject="acme.com")), 0)
        self.assertEqual(len(self.store.recall(subject="other.com")), 1)

    def test_persists_across_new_store_instances(self):
        """Simulates a fresh process reading the same memory file — this is
        the actual 'continuous learning survives restarts' guarantee."""
        self.store.remember(MemoryCategory.REDESIGN_OUTCOME, "acme.com", {"result": "success"})

        reopened_store = MemoryStore(path=str(self.store.path))
        results = reopened_store.recall(subject="acme.com")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content["result"], "success")

    def test_corrupted_line_does_not_break_recall(self):
        # Write one valid record, then manually corrupt the file with a
        # broken line, then write another valid record.
        self.store.remember(MemoryCategory.BRAND_PROFILE, "acme.com", {"ok": 1})
        with open(self.store.path, "a", encoding="utf-8") as f:
            f.write("{not valid json\n")
        self.store.remember(MemoryCategory.BRAND_PROFILE, "acme.com", {"ok": 2})

        results = self.store.recall(subject="acme.com")
        self.assertEqual(len(results), 2)

    def test_stats_reports_totals_by_category(self):
        self.store.remember(MemoryCategory.BRAND_PROFILE, "a.com", {})
        self.store.remember(MemoryCategory.BRAND_PROFILE, "b.com", {})
        self.store.remember(MemoryCategory.SITE_INSPECTION, "a.com", {})

        stats = self.store.stats()
        self.assertEqual(stats["total_memories"], 3)
        self.assertEqual(stats["by_category"][MemoryCategory.BRAND_PROFILE], 2)
        self.assertEqual(stats["unique_subjects"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
