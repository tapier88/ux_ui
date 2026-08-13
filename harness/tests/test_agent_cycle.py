"""
Tests for the deterministic Fase 3 agent cycle.

The cycle wraps DesignPipelineNode in explicit PLAN -> EXECUTE -> OBSERVE ->
EVALUATE -> DECIDE phases without requiring an external LLM provider.
"""
import os
import shutil
import tempfile
import unittest

FIXTURE_SOURCE = os.path.join(
    os.path.dirname(__file__), "fixtures", "sample_project"
)


class AgentCycleTestCase(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.mkdtemp(prefix="agent_cycle_")
        shutil.copytree(FIXTURE_SOURCE, self.work_dir, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def _list_files(self):
        found = []
        for root, dirs, files in os.walk(self.work_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in files:
                found.append(os.path.relpath(os.path.join(root, f), self.work_dir))
        return found


class TestDeterministicDesignAgent(AgentCycleTestCase):
    def test_dry_run_stops_ready_to_execute_without_writing(self):
        from harness.agents import AgentDecision, DeterministicDesignAgent

        files_before = set(self._list_files())
        result = DeterministicDesignAgent().run(
            project_path=self.work_dir,
            task_id="agent-cycle-dry-run",
            url="https://example.com",
            execute=False,
        )
        files_after = set(self._list_files())

        self.assertEqual(result.decision, AgentDecision.READY_TO_EXECUTE)
        self.assertEqual(files_before, files_after)
        self.assertEqual(
            [step.phase for step in result.trace],
            ["PLAN", "EXECUTE", "OBSERVE", "EVALUATE", "DECIDE"],
        )
        self.assertTrue(result.dry_run_result["governance"]["passed"])
        self.assertIsNone(result.build_result)

    def test_execute_true_runs_real_build_after_approved_dry_run(self):
        from harness.agents import AgentDecision, DeterministicDesignAgent

        result = DeterministicDesignAgent().run(
            project_path=self.work_dir,
            task_id="agent-cycle-build",
            url="https://example.com",
            execute=True,
        )

        self.assertEqual(result.decision, AgentDecision.COMPLETE)
        self.assertIsNotNone(result.build_result)
        self.assertEqual(result.build_result["status"], "completed")
        self.assertIn("src/components/Navigation.tsx", result.build_result["report"]["files_created"])
        self.assertEqual(
            [step.phase for step in result.trace],
            [
                "PLAN",
                "EXECUTE",
                "OBSERVE",
                "EVALUATE",
                "DECIDE",
                "EXECUTE",
                "OBSERVE",
                "EVALUATE",
                "DECIDE",
            ],
        )

    def test_governance_failure_blocks_before_real_build(self):
        from harness.agents import AgentDecision, DeterministicDesignAgent

        files_before = set(self._list_files())
        result = DeterministicDesignAgent().run(
            project_path=self.work_dir,
            task_id="agent-cycle-blocked",
            url="https://example.com",
            execute=True,
            governance_threshold=101.0,
        )
        files_after = set(self._list_files())

        self.assertEqual(result.decision, AgentDecision.BLOCKED)
        self.assertEqual(files_before, files_after)
        self.assertIsNone(result.build_result)
        self.assertEqual(result.trace[-1].phase, "DECIDE")
        self.assertEqual(result.trace[-1].status, AgentDecision.BLOCKED)

    def test_retry_can_recover_from_over_strict_governance_threshold(self):
        from harness.agents import AgentDecision, DeterministicDesignAgent

        result = DeterministicDesignAgent().run(
            project_path=self.work_dir,
            task_id="agent-cycle-retry",
            url="https://example.com",
            execute=False,
            governance_threshold=101.0,
            max_iterations=2,
        )

        self.assertEqual(result.decision, AgentDecision.READY_TO_EXECUTE)
        self.assertEqual(
            [step.status for step in result.trace if step.phase == "DECIDE"],
            ["retry", AgentDecision.READY_TO_EXECUTE],
        )
        plan_steps = [step for step in result.trace if step.phase == "PLAN"]
        self.assertEqual(len(plan_steps), 2)
        self.assertLess(
            plan_steps[1].data["governance_threshold"],
            plan_steps[0].data["governance_threshold"],
        )

    def test_retry_limit_blocks_when_no_passing_iteration_exists(self):
        from harness.agents import AgentDecision, DeterministicDesignAgent

        result = DeterministicDesignAgent().run(
            project_path=self.work_dir,
            task_id="agent-cycle-retry-limit",
            url="https://example.com",
            execute=False,
            governance_threshold=101.0,
            max_iterations=1,
        )

        self.assertEqual(result.decision, AgentDecision.BLOCKED)
        self.assertEqual(
            [step.phase for step in result.trace],
            ["PLAN", "EXECUTE", "OBSERVE", "EVALUATE", "DECIDE"],
        )
        self.assertEqual(result.trace[-1].status, AgentDecision.BLOCKED)


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDeterministicDesignAgent))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
