"""
Tests for deterministic SEO analysis skill.
"""
import os
import shutil
import tempfile
import unittest


class TestSEOAnalysis(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.mkdtemp(prefix="seo_analysis_")

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def _build_plan(self):
        return {
            "pages": [
                {
                    "name": "Home",
                    "seo_requirements": {
                        "title": "Home | Example",
                        "description": "Example landing page",
                        "og_image": True,
                    },
                }
            ],
            "sections": [
                {"name": "Hero"},
                {"name": "Proof"},
                {"name": "CTA"},
            ],
            "performance_plan": {
                "lazy_loading": True,
            },
        }

    def test_high_quality_plan_scores_high(self):
        from harness.skills.seo_analysis import SEOAnalysisEngine

        with open(os.path.join(self.work_dir, "robots.txt"), "w") as f:
            f.write("User-agent: *\nAllow: /\n")

        report = SEOAnalysisEngine().analyze(
            profile={},
            build_plan=self._build_plan(),
            project_path=self.work_dir,
        )

        self.assertEqual(report.score, 100.0)
        self.assertEqual(report.recommendations, [])

    def test_missing_metadata_returns_recommendations(self):
        from harness.skills.seo_analysis import seo_analysis_skill

        result = seo_analysis_skill(
            build_plan={
                "pages": [{"name": "Home", "seo_requirements": {}}],
                "sections": [{"name": ""}],
                "performance_plan": {},
            },
            project_path=self.work_dir,
        )

        self.assertLess(result["score"], 75.0)
        self.assertGreater(len(result["recommendations"]), 0)
        self.assertIn("page_titles", [check["name"] for check in result["checks"]])

    def test_skill_registry_auto_registers_seo_analysis(self):
        from harness.skills import get_skill_registry, register_seo_analysis_skill

        registry = get_skill_registry()
        register_seo_analysis_skill()

        self.assertTrue(registry.has_skill("seo-analysis"))
        self.assertTrue(registry.is_skill_loaded("seo-analysis"))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSEOAnalysis))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
