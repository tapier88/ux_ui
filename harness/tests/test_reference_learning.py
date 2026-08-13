"""
Tests for reference learning skill.
"""
import unittest


class TestReferenceLearning(unittest.TestCase):
    def _references(self):
        return [
            {
                "title": "Restaurant landing page with testimonials",
                "summary": "Hero CTA, logo cloud, testimonial cards, and book now action.",
                "tags": ["landing", "social proof", "cta"],
            },
            {
                "title": "Accessible card interface",
                "summary": "Strong contrast, keyboard support, aria labels, and reduced motion.",
                "tags": ["accessibility", "cards"],
            },
        ]

    def test_extracts_lessons_from_reference_text(self):
        from harness.skills.reference_learning import ReferenceLearningEngine

        report = ReferenceLearningEngine().learn(
            references=self._references(),
            project_context={"project_type": "landing"},
        )

        patterns = [lesson.pattern for lesson in report.lessons]
        self.assertIn("conversion_cta", patterns)
        self.assertIn("social_proof", patterns)
        self.assertIn("accessibility", patterns)
        self.assertEqual(report.references_used, 2)

    def test_skill_returns_serializable_lessons(self):
        from harness.skills.reference_learning import reference_learning_skill

        result = reference_learning_skill(
            references=self._references(),
            project_context={"project_type": "landing"},
        )

        self.assertGreater(len(result["lessons"]), 0)
        self.assertIn("recommendation", result["lessons"][0])

    def test_skill_registry_registers_reference_learning(self):
        from harness.skills import get_skill_registry, register_reference_learning_skill

        registry = get_skill_registry()
        register_reference_learning_skill()

        self.assertTrue(registry.has_skill("reference-learning"))
        self.assertTrue(registry.is_skill_loaded("reference-learning"))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceLearning))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
