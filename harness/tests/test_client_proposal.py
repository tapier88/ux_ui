"""
Tests for client proposal generation.
"""
import unittest


class TestClientProposal(unittest.TestCase):
    def _inputs(self):
        return {
            "profile": {
                "project_name": "sample_project",
                "visual_design": None,
                "accessibility": None,
                "performance": None,
            },
            "build_plan": {
                "sections": [{"name": "Hero"}, {"name": "Proof"}],
                "components": [{"name": "Button"}, {"name": "Card"}],
            },
            "seo": {
                "score": 83.33,
                "checks": [
                    {"name": "page_titles", "passed": True},
                    {"name": "indexability_hints", "passed": False},
                ],
                "recommendations": ["Add robots.txt or sitemap.xml for crawler guidance."],
            },
            "governance": {
                "passed": True,
                "total_score": 88.0,
                "signals": [
                    {
                        "name": "seo_impact",
                        "score": 83.33,
                        "evidence": "5/6 SEO checks passed",
                    }
                ],
            },
        }

    def test_generates_client_facing_markdown(self):
        from harness.skills.client_proposal import ClientProposalGenerator

        proposal = ClientProposalGenerator().generate(**self._inputs())

        self.assertEqual(proposal.title, "Redesign proposal for sample_project")
        self.assertIn("## Before", proposal.markdown)
        self.assertIn("## After", proposal.markdown)
        self.assertIn("## SEO impact", proposal.markdown)
        self.assertIn("83.33/100", proposal.markdown)

    def test_skill_returns_serializable_dict(self):
        from harness.skills.client_proposal import client_proposal_skill

        result = client_proposal_skill(**self._inputs())

        self.assertIn("markdown", result)
        self.assertIn("seo_impact", result)
        self.assertGreater(len(result["proof_points"]), 0)

    def test_skill_registry_registers_client_proposal(self):
        from harness.skills import get_skill_registry, register_client_proposal_skill

        registry = get_skill_registry()
        register_client_proposal_skill()

        self.assertTrue(registry.has_skill("client-proposal"))
        self.assertTrue(registry.is_skill_loaded("client-proposal"))


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestClientProposal))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
