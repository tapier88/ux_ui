"""
Tests for provider-agnostic design judgment engine.
"""
import unittest

from harness.agents import LLMProvider, LLMResponse, ProviderStatus


class StaticProvider(LLMProvider):
    def __init__(self, content: str):
        self.content = content
        self.requests = []

    def connect(self) -> bool:
        return True

    def disconnect(self):
        pass

    def is_connected(self) -> bool:
        return True

    def generate(self, request):
        self.requests.append(request)
        return LLMResponse(
            content=self.content,
            metadata={"provider": "static-test"},
        )

    def get_status(self) -> ProviderStatus:
        return ProviderStatus.MOCK


class TestDesignJudgmentEngine(unittest.TestCase):
    def test_builds_prompt_from_structured_request(self):
        from harness.agents import BaseDesignJudgmentEngine, DesignJudgmentRequest

        provider = StaticProvider("approve: layout is clear")
        engine = BaseDesignJudgmentEngine(provider=provider)

        result = engine.judge(
            DesignJudgmentRequest(
                judgment_type="hero_section_review",
                subject="landing page hero",
                criteria=["clear hierarchy", "accessible contrast"],
                context={"industry": "finance", "primary_color": "#2563EB"},
                metadata={"task_id": "judgment-test"},
            )
        )

        prompt = provider.requests[0].prompt
        self.assertIn("Judgment type: hero_section_review", prompt)
        self.assertIn("Subject: landing page hero", prompt)
        self.assertIn("- accessible contrast", prompt)
        self.assertIn("- industry: finance", prompt)
        self.assertEqual(result.decision, "approve")
        self.assertEqual(result.provider_status, "mock")
        self.assertEqual(result.metadata["task_id"], "judgment-test")

    def test_rejects_invalid_requests(self):
        from harness.agents import BaseDesignJudgmentEngine, DesignJudgmentRequest

        engine = BaseDesignJudgmentEngine(provider=StaticProvider("review"))

        with self.assertRaises(ValueError):
            engine.judge(DesignJudgmentRequest(judgment_type="", subject="hero"))

        with self.assertRaises(ValueError):
            engine.judge(DesignJudgmentRequest(judgment_type="review", subject=""))

    def test_default_parser_normalizes_blocking_language(self):
        from harness.agents import BaseDesignJudgmentEngine, DesignJudgmentRequest

        engine = BaseDesignJudgmentEngine(
            provider=StaticProvider("blocked: contrast fails accessibility")
        )

        result = engine.judge(
            DesignJudgmentRequest(
                judgment_type="accessibility_review",
                subject="pricing cards",
            )
        )

        self.assertEqual(result.decision, "reject")
        self.assertGreaterEqual(result.confidence, 0.7)

    def test_result_serializes_to_dict(self):
        from harness.agents import BaseDesignJudgmentEngine, DesignJudgmentRequest

        engine = BaseDesignJudgmentEngine(provider=StaticProvider("needs review"))
        result = engine.judge(
            DesignJudgmentRequest(judgment_type="visual_review", subject="navbar")
        )

        result_dict = result.to_dict()
        self.assertEqual(result_dict["decision"], "review")
        self.assertIn("rationale", result_dict)
        self.assertIn("raw_response", result_dict)


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDesignJudgmentEngine))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
