"""
Tests for harness.nodes.design_pipeline_nodes — the FASE 1 end-to-end
graph that wires all 5 design skills together (previously each skill
only worked in isolation, called by hand).

These tests run the REAL pipeline against a synthetic project on disk —
no mocking of the skills — because the whole point of FASE 1 was
discovering and fixing the integration bugs that only show up when the
skills actually run together (see ROADMAP.md FASE 1 changelog for the
7 bugs this surfaced).

Run with: python -m unittest harness.tests.test_design_pipeline_nodes -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from harness.core.runtime import GraphRuntime
from harness.core.state import get_state_manager
from harness.nodes.design_pipeline_nodes import (
    build_design_pipeline_graph,
    SiteBuilderNode,
)


def make_test_project(root: Path, primary_color: str = "#2563EB"):
    (root / "index.html").write_text(
        "<!DOCTYPE html><html><head><title>Acme</title></head>"
        "<body><h1>Acme Corp</h1><p>Welcome</p></body></html>",
        encoding="utf-8",
    )
    (root / "style.css").write_text(f"body {{ margin: 0; color: {primary_color}; }}", encoding="utf-8")


class TestPipelineGraphStructure(unittest.TestCase):

    def test_graph_is_valid(self):
        graph = build_design_pipeline_graph()
        is_valid, errors = graph.validate()
        self.assertTrue(is_valid, msg=f"Graph validation errors: {errors}")

    def test_graph_has_all_expected_nodes(self):
        graph = build_design_pipeline_graph()
        expected = {
            "START", "WEBSITE_INTELLIGENCE_NODE", "REDESIGN_INTELLIGENCE_NODE",
            "DESIGN_RESOURCE_HUB_NODE", "DESIGN_EXECUTION_PLANNER_NODE",
            "GOVERNANCE_GATE_NODE", "SITE_BUILDER_NODE", "END",
        }
        self.assertEqual(set(graph.nodes.keys()), expected)


class TestPipelineApprovedPath(unittest.TestCase):
    """A project with a real brand color should clear the gate and
    produce real, valid file output."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_pipeline_test_")
        make_test_project(Path(self.tmp_dir))
        get_state_manager().clear_all()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _run(self, task_id: str, threshold: float = 60.0):
        graph = build_design_pipeline_graph(governance_threshold=threshold)
        runtime = GraphRuntime()
        return runtime.execute(
            graph, task_id,
            initial_state={"project_path": self.tmp_dir, "project_name": "acme_test"},
        )

    def test_full_pipeline_runs_to_completion(self):
        result = self._run("approved_path_task")
        self.assertTrue(result.success, msg=f"errors: {result.errors}")
        self.assertIn("SITE_BUILDER_NODE", result.nodes_executed)

    def test_governance_gate_passed(self):
        self._run("gate_passed_task")
        state = get_state_manager().get_state("gate_passed_task")
        gate_result = state.outputs["GOVERNANCE_GATE_NODE"]
        self.assertTrue(gate_result["passed"])

    def test_site_builder_produces_valid_css_not_python_repr(self):
        self._run("valid_css_task")
        tokens_css = Path(self.tmp_dir) / "src" / "styles" / "tokens.css"
        self.assertTrue(tokens_css.exists())
        content = tokens_css.read_text(encoding="utf-8")
        # This is the regression check for the "dumped Python dict repr
        # as a CSS value" bug found during FASE 1 integration testing.
        self.assertNotIn("{'", content)
        self.assertIn("--colors-primary:", content)

    def test_site_builder_produces_component_files_with_clean_names(self):
        self._run("clean_names_task")
        sections_dir = Path(self.tmp_dir) / "src" / "components" / "sections"
        self.assertTrue(sections_dir.exists())
        for path in sections_dir.glob("*.tsx"):
            self.assertNotIn(" ", path.name, msg="Component filenames must not contain spaces")

    def test_build_report_recorded_in_state(self):
        self._run("report_recorded_task")
        state = get_state_manager().get_state("report_recorded_task")
        report = state.outputs["SITE_BUILDER_NODE"]
        self.assertEqual(report["build_status"], "pass")
        self.assertEqual(report["errors"], [])


class TestPipelineBlockedPath(unittest.TestCase):
    """A project with no clear brand signal (or an artificially high
    threshold) must be blocked before Site Builder ever touches disk."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="harness_pipeline_blocked_test_")
        # Deliberately minimal project with no color information at all.
        (Path(self.tmp_dir) / "index.html").write_text(
            "<!DOCTYPE html><html><body><h1>Test</h1></body></html>", encoding="utf-8"
        )
        get_state_manager().clear_all()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_high_threshold_blocks_before_site_builder(self):
        graph = build_design_pipeline_graph(governance_threshold=99.9)
        runtime = GraphRuntime()
        result = runtime.execute(
            graph, "blocked_task",
            initial_state={"project_path": self.tmp_dir, "project_name": "blocked_test"},
        )

        self.assertNotIn("SITE_BUILDER_NODE", result.nodes_executed)

        state = get_state_manager().get_state("blocked_task")
        self.assertFalse(state.outputs["GOVERNANCE_GATE_NODE"]["passed"])

    def test_blocked_pipeline_leaves_project_untouched(self):
        graph = build_design_pipeline_graph(governance_threshold=99.9)
        runtime = GraphRuntime()
        runtime.execute(
            graph, "untouched_task",
            initial_state={"project_path": self.tmp_dir, "project_name": "untouched_test"},
        )

        files = list(Path(self.tmp_dir).rglob("*"))
        self.assertEqual(len(files), 1)  # only the original index.html
        self.assertEqual(files[0].name, "index.html")


class TestImplementationOrderTranslation(unittest.TestCase):
    """Regression coverage for the DesignExecutionPlanner -> SiteBuilder
    vocabulary mismatch found during FASE 1 integration testing."""

    def test_translates_descriptive_task_names_to_step_ids(self):
        raw_order = [
            {"task": "Project setup"},
            {"task": "Design tokens"},
            {"task": "Hero section"},
            {"task": "Content sections"},
            {"task": "Quality validation"},
        ]
        translated = SiteBuilderNode._translate_implementation_order(raw_order)
        self.assertIn("dependencies", translated)
        self.assertIn("tokens", translated)
        self.assertIn("sections", translated)
        self.assertIn("validation", translated)
        # "Hero section" and "Content sections" must not produce duplicate
        # "sections" entries.
        self.assertEqual(translated.count("sections"), 1)

    def test_unrecognized_task_names_are_dropped_not_crashed(self):
        raw_order = [{"task": "Some totally unknown future step"}]
        translated = SiteBuilderNode._translate_implementation_order(raw_order)
        self.assertEqual(translated, [])

    def test_handles_plain_strings_as_well_as_task_dicts(self):
        translated = SiteBuilderNode._translate_implementation_order(["tokens", "typography"])
        self.assertEqual(translated, ["tokens", "typography"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
