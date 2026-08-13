"""
Integration test for the full 5-stage design pipeline
(website_intelligence -> redesign_intelligence -> design_resource_hub ->
design_execution_planner -> site_builder), run end-to-end through
DesignPipelineNode against a fixed, version-controlled fixture project.

Why this exists: each of the 5 skills has its own isolated unit-test suite
with hand-built fixtures that happen to match what that skill expects. None
of them were ever tested against the *actual* output of the skill before it
in the chain. That let five separate contract mismatches ship unnoticed
(see PLAN.md Fase 2 for the full list). This test is the regression guard
so a sixth one doesn't ship the same way.

Uses a copy of harness/tests/fixtures/sample_project/ in a temp directory
per test (never mutates the checked-in fixture), so runs are reproducible
across machines and sessions.
"""
import os
import shutil
import tempfile
import unittest

FIXTURE_SOURCE = os.path.join(
    os.path.dirname(__file__), "fixtures", "sample_project"
)


class DesignPipelineIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.mkdtemp(prefix="pipeline_integration_")
        shutil.copytree(FIXTURE_SOURCE, self.work_dir, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def _run_pipeline(self, dry_run):
        from harness.nodes.design_pipeline_node import DesignPipelineNode
        from harness.core.state import TaskState

        state = TaskState(task_id="integration-test")
        state.inputs = {
            "project_path": self.work_dir,
            "url": "https://example.com",
            "dry_run": dry_run,
        }
        return DesignPipelineNode().execute(state)


class TestDryRun(DesignPipelineIntegrationTestCase):
    def test_01_dry_run_completes_all_four_planning_stages(self):
        """The first 4 stages (everything before site_builder) succeed and
        produce a build plan, without writing anything to disk."""
        result = self._run_pipeline(dry_run=True)

        self.assertEqual(result["status"], "dry_run_completed", result)
        for stage in (
            "website_intelligence",
            "redesign_intelligence",
            "design_resource_hub",
            "design_execution_planner",
        ):
            self.assertEqual(
                result["stages"][stage]["status"], "completed", stage
            )
        self.assertIn("build_plan", result)
        self.assertGreater(len(result["build_plan"].get("sections", [])), 0)
        self.assertIn("navigation", result["build_plan"])
        self.assertGreater(len(result["build_plan"]["navigation"].get("items", [])), 0)
        self.assertIn("interactions", result["build_plan"])
        self.assertGreater(len(result["build_plan"]["interactions"]), 0)

    def test_02_dry_run_does_not_touch_disk(self):
        """dry_run=True must be a real dry run: no new files."""
        files_before = set(self._list_files())
        self._run_pipeline(dry_run=True)
        files_after = set(self._list_files())
        self.assertEqual(files_before, files_after)

    def _list_files(self):
        found = []
        for root, dirs, files in os.walk(self.work_dir):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in files:
                found.append(os.path.relpath(os.path.join(root, f), self.work_dir))
        return found


class TestRealBuild(DesignPipelineIntegrationTestCase):
    def test_03_real_build_completes_without_errors(self):
        """The full pipeline, including site_builder actually writing
        files, must complete with an empty errors list. This is the test
        that first caught: typography=None crash, BuildError not imported,
        DesignBuildPlan object-vs-dict, implementation_order dict-vs-string,
        and RemoveEngine patterns list-vs-dict."""
        result = self._run_pipeline(dry_run=False)

        self.assertEqual(result["status"], "completed", result)
        report = result["report"]
        self.assertEqual(
            report.get("errors"), [], f"Build reported errors: {report.get('errors')}"
        )
        self.assertEqual(report.get("build_status"), "pass", report)

    def test_04_real_build_writes_at_least_one_real_file(self):
        """A pipeline that 'completes successfully' but writes nothing is a
        hollow success - this asserts real output, not just the absence of
        an exception."""
        result = self._run_pipeline(dry_run=False)
        report = result["report"]
        total_output = len(report.get("files_created", [])) + len(
            report.get("files_modified", [])
        )
        self.assertGreater(
            total_output, 0, "Build completed but created/modified 0 files"
        )

    def test_05_real_build_writes_navigation_and_interaction_outputs(self):
        """Navigation and interactions are explicit implementation steps,
        so they must produce real artifacts instead of pass-through no-ops."""
        result = self._run_pipeline(dry_run=False)
        report = result["report"]
        created = set(report.get("files_created", []))

        self.assertIn("src/components/Navigation.tsx", created)
        self.assertIn("NAVIGATION_PLAN.md", created)
        self.assertIn("INTERACTIONS_PLAN.md", created)

    def test_06_running_twice_in_a_row_is_stable(self):
        """Regression test for the WebsiteInspector non-determinism found
        while debugging this pipeline: running the build twice on what
        should be the same project (the harness's own checkpoint/output
        directories must not be picked up as project content on the second
        inspection) must not change the outcome from pass to fail."""
        first = self._run_pipeline(dry_run=False)
        second = self._run_pipeline(dry_run=False)

        self.assertEqual(first["status"], "completed", first)
        self.assertEqual(second["status"], "completed", second)
        self.assertEqual(
            first["report"].get("build_status"),
            second["report"].get("build_status"),
            "Build status changed between two consecutive runs on the same project",
        )
        self.assertEqual(
            second["report"].get("errors"),
            [],
            f"Second run reported errors: {second['report'].get('errors')}",
        )


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDryRun))
    suite.addTests(loader.loadTestsFromTestCase(TestRealBuild))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
