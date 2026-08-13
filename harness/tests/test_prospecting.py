"""
Tests for prospecting skill.
"""
import unittest


class TestProspecting(unittest.TestCase):
    def _candidates(self):
        return [
            {
                "url": "https://old-restaurant.example",
                "business_name": "Old Restaurant",
                "industry": "restaurant",
                "stack": ["jquery", "bootstrap 3"],
                "mobile_score": 35,
                "seo_score": 45,
                "accessibility_score": 40,
            },
            {
                "url": "https://modern-saas.example",
                "business_name": "Modern SaaS",
                "industry": "saas",
                "stack": ["next.js", "tailwind"],
                "mobile_score": 95,
                "seo_score": 92,
                "accessibility_score": 90,
            },
        ]

    def test_ranks_highest_redesign_opportunity_first(self):
        from harness.skills.prospecting import ProspectingEngine

        ranked = ProspectingEngine().rank(self._candidates())

        self.assertEqual(ranked[0].business_name, "Old Restaurant")
        self.assertGreater(ranked[0].score, ranked[1].score)
        self.assertGreater(len(ranked[0].reasons), 0)

    def test_skill_returns_serializable_candidates(self):
        from harness.skills.prospecting import prospecting_skill

        result = prospecting_skill(self._candidates(), limit=1)

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["candidates"][0]["business_name"], "Old Restaurant")
        self.assertIn("signals", result["candidates"][0])

    def test_skill_registry_registers_prospecting(self):
        from harness.skills import get_skill_registry, register_prospecting_skill

        registry = get_skill_registry()
        register_prospecting_skill()

        self.assertTrue(registry.has_skill("prospecting"))
        self.assertTrue(registry.is_skill_loaded("prospecting"))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestProspecting))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
