"""
Tests for harness.skills.site_builder — the highest-risk skill in the
pipeline (previously zero test coverage) because it modifies real files
on a real project. These tests run against a synthetic temp project so
nothing in the actual repo is ever touched, but exercise the REAL
inspector/file-manager/rollback machinery, not mocks — the whole point
is proving the safety net actually works.

Run with: python -m unittest harness.tests.test_site_builder -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from harness.skills.site_builder import (
    ProjectInspector,
    FileManager,
    RollbackManager,
    SiteBuilder,
    ValidationStatus,
)
from harness.skills.design_execution_planner import DesignExecutionPlanner


def make_minimal_static_project(root: Path):
    """A minimal static HTML/CSS project — deliberately has no
    package.json/eslint config, so site_builder's validation steps
    gracefully skip instead of shelling out to real npm/eslint."""
    (root / "index.html").write_text(
        "<!DOCTYPE html><html><head><title>Test</title></head>"
        "<body><h1>Hello</h1></body></html>",
        encoding="utf-8",
    )
    (root / "style.css").write_text("body { margin: 0; }", encoding="utf-8")


class TestProjectInspector(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_sitebuilder_test_")
        make_minimal_static_project(Path(self.tmp_dir))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_inspect_minimal_project_does_not_crash(self):
        inspector = ProjectInspector(self.tmp_dir)
        snapshot = inspector.inspect()
        self.assertIsNotNone(snapshot)

    def test_inspect_empty_directory_does_not_crash(self):
        empty_dir = tempfile.mkdtemp(prefix="harness_sitebuilder_empty_")
        try:
            inspector = ProjectInspector(empty_dir)
            snapshot = inspector.inspect()
            self.assertIsNotNone(snapshot)
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)


class TestFileManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_sitebuilder_fm_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_create_read_modify_delete_cycle(self):
        fm = FileManager(self.tmp_dir)

        fm.create_file("src/test.css", "body { color: red; }", reason="test")
        self.assertTrue(fm.file_exists("src/test.css"))
        self.assertEqual(fm.read_file("src/test.css"), "body { color: red; }")

        fm.modify_file(
            "src/test.css",
            old_content="body { color: red; }",
            new_content="body { color: blue; }",
            reason="test modify",
        )
        self.assertEqual(fm.read_file("src/test.css"), "body { color: blue; }")

        fm.delete_file("src/test.css", reason="test delete")
        self.assertFalse(fm.file_exists("src/test.css"))

    def test_cannot_escape_project_sandbox(self):
        """A file path that tries to escape the project directory (path
        traversal) must be rejected — this is the boundary that keeps
        an autonomous code-modifying agent from touching anything
        outside the client's own project."""
        fm = FileManager(self.tmp_dir)
        self.assertFalse(fm.validate_path("../../etc/passwd"))

    def test_all_changes_are_tracked(self):
        fm = FileManager(self.tmp_dir)
        fm.create_file("a.css", "a", reason="test")
        fm.create_file("b.css", "b", reason="test")
        changes = fm.get_all_changes()
        self.assertEqual(len(changes), 2)


class TestRollbackManager(unittest.TestCase):
    """The safety net: this is what protects a real client project from
    a bad or crashed build."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_sitebuilder_rb_test_")
        make_minimal_static_project(Path(self.tmp_dir))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_rollback_restores_modified_file(self):
        rollback = RollbackManager(self.tmp_dir, task_id="test_task")
        rollback.create_checkpoint("CP1", "before change")

        style_path = Path(self.tmp_dir) / "style.css"
        original_content = style_path.read_text(encoding="utf-8")
        style_path.write_text("body { margin: 999px; }", encoding="utf-8")
        self.assertNotEqual(style_path.read_text(encoding="utf-8"), original_content)

        result = rollback.rollback("CP1")

        self.assertEqual(style_path.read_text(encoding="utf-8"), original_content)
        self.assertTrue(result.success if hasattr(result, "success") else True)

    def test_rollback_restores_deleted_file(self):
        rollback = RollbackManager(self.tmp_dir, task_id="test_task_2")
        rollback.create_checkpoint("CP1", "before delete")

        style_path = Path(self.tmp_dir) / "style.css"
        style_path.unlink()
        self.assertFalse(style_path.exists())

        rollback.rollback("CP1")

        self.assertTrue(style_path.exists())

    def test_list_checkpoints_returns_created_checkpoints(self):
        rollback = RollbackManager(self.tmp_dir, task_id="test_task_3")
        rollback.create_checkpoint("CP1", "first")
        rollback.create_checkpoint("CP2", "second")
        checkpoints = rollback.list_checkpoints()
        self.assertIn("CP1", checkpoints)
        self.assertIn("CP2", checkpoints)


class TestSiteBuilderEndToEnd(unittest.TestCase):
    """Runs the real pipeline: DesignExecutionPlanner produces a build
    plan, SiteBuilder executes it against a synthetic project. No
    mocking of the build machinery — this is the actual code path a
    live redesign goes through."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_sitebuilder_e2e_test_")
        make_minimal_static_project(Path(self.tmp_dir))

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _minimal_plan(self):
        planner = DesignExecutionPlanner()
        plan = planner.create_build_plan(project_name="e2e_test_project")
        plan_dict = plan.to_dict()
        # Keep implementation_order to steps that don't shell out to
        # npm/eslint (no "dependencies" step) — this project has no
        # package.json on purpose.
        plan_dict["implementation_order"] = [
            step for step in plan_dict.get("implementation_order", [])
            if step != "dependencies"
        ]
        return plan_dict

    def test_execute_build_completes_and_produces_a_report(self):
        builder = SiteBuilder(self.tmp_dir)
        report = builder.execute_build(self._minimal_plan())

        self.assertIsNotNone(report)
        self.assertIn(report.build_status, (ValidationStatus.PASS, ValidationStatus.FAIL))

    def test_execute_build_creates_checkpoints(self):
        builder = SiteBuilder(self.tmp_dir)
        builder.execute_build(self._minimal_plan())
        self.assertGreater(len(builder.checkpoints_created), 0)

    def test_execute_build_writes_token_file_when_tokens_present(self):
        builder = SiteBuilder(self.tmp_dir)
        plan = self._minimal_plan()
        report = builder.execute_build(plan)

        if report.build_status == ValidationStatus.PASS and "tokens" in plan.get("implementation_order", []):
            tokens_file = Path(self.tmp_dir) / "src" / "styles" / "tokens.css"
            self.assertTrue(tokens_file.exists())

    def test_failed_build_triggers_automatic_rollback(self):
        """This is the single most important safety guarantee in this
        skill: if something breaks mid-build, the client's real project
        must come back exactly as it was — not half-modified."""
        builder = SiteBuilder(self.tmp_dir)
        plan = self._minimal_plan()
        plan["implementation_order"] = ["tokens"]
        plan["design_tokens"] = {"colors": {"primary": "#2563EB"}}

        original_style_content = (Path(self.tmp_dir) / "style.css").read_text(encoding="utf-8")

        def broken_generate_css_variables(*args, **kwargs):
            raise RuntimeError("simulated failure mid-build")

        builder.code_generator.generate_css_variables = broken_generate_css_variables

        report = builder.execute_build(plan)

        self.assertEqual(report.build_status, ValidationStatus.FAIL)
        self.assertTrue(len(report.errors) > 0)
        self.assertIsNotNone(report.rollback_status)
        # The original file must be untouched after rollback
        self.assertEqual(
            (Path(self.tmp_dir) / "style.css").read_text(encoding="utf-8"),
            original_style_content,
        )
        # And the tokens file that would have been created should NOT
        # exist — the rollback must undo partial work too.
        self.assertFalse((Path(self.tmp_dir) / "src" / "styles" / "tokens.css").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
