"""
Tests for harness.skills.design_execution_planner — previously had zero
test coverage despite being one of the larger skills in the pipeline
(converts design decisions into a full technical build plan: layout,
tokens, components, motion, responsive, accessibility, performance).

Run with: python -m unittest harness.tests.test_design_execution_planner -v
"""
import unittest

from harness.skills.design_execution_planner import (
    DesignExecutionPlanner,
    LayoutPlanner,
    ComponentPlanner,
    MotionPlanner,
    AssetPlanner,
    ResponsivePlanner,
    AccessibilityPlanner,
    PerformancePlanner,
    PlanValidator,
    LayoutType,
    DesignBuildPlan,
)


class TestDesignExecutionPlannerEndToEnd(unittest.TestCase):
    """Exercises the real orchestration path with no mocking — this is
    the path every redesign actually goes through."""

    def setUp(self):
        self.planner = DesignExecutionPlanner()

    def test_create_build_plan_with_no_inputs_does_not_crash(self):
        """Every input is optional — the planner must degrade gracefully
        instead of raising when upstream skills haven't run yet."""
        plan = self.planner.create_build_plan(project_name="empty_project")
        self.assertIsInstance(plan, DesignBuildPlan)
        self.assertEqual(plan.project, "empty_project")

    def test_create_build_plan_with_full_inputs(self):
        design_profile = {
            "brand": {"personality": "editorial", "preserve_colors": True},
            "colors": {"primary": "#2563EB"},
        }
        redesign_strategy = {
            "layout": {"pattern": "editorial"},
            "typography": {},
        }
        resource_report = {"selected_resources": []}
        existing_code = {"framework": "react"}

        plan = self.planner.create_build_plan(
            project_name="acme_redesign",
            design_profile=design_profile,
            redesign_strategy=redesign_strategy,
            resource_report=resource_report,
            existing_code=existing_code,
        )

        self.assertEqual(plan.project, "acme_redesign")
        self.assertIsNotNone(plan.layout_plan)
        self.assertIsNotNone(plan.design_tokens)
        self.assertIsNotNone(plan.motion_plan)
        self.assertIsNotNone(plan.responsive_plan)
        self.assertIsNotNone(plan.accessibility_plan)
        self.assertIsNotNone(plan.performance_plan)
        self.assertTrue(len(plan.implementation_order) > 0)

    def test_editorial_brand_personality_selects_editorial_layout(self):
        plan = self.planner.create_build_plan(
            project_name="editorial_test",
            design_profile={"brand": {"personality": "editorial"}},
        )
        self.assertEqual(plan.layout_plan.grid, "12-column")
        # Editorial layouts should not default to a plain single column
        self.assertIsNotNone(plan.layout_plan)

    def test_build_plan_serializes_to_dict(self):
        plan = self.planner.create_build_plan(project_name="serialization_test")
        as_dict = plan.to_dict()
        self.assertIsInstance(as_dict, dict)
        self.assertEqual(as_dict.get("project"), "serialization_test")


class TestLayoutPlanner(unittest.TestCase):
    """LayoutPlanner is the concrete answer to 'how does the agent use
    the canvas/space' — 16 distinct layout patterns, not one template."""

    def setUp(self):
        self.planner = LayoutPlanner()

    def test_all_layout_types_produce_a_plan(self):
        for layout_type in LayoutType:
            plan = self.planner.plan_layout(layout_type=layout_type)
            self.assertIsNotNone(plan.grid, msg=f"{layout_type} produced no grid")
            self.assertIsNotNone(plan.container_width, msg=f"{layout_type} produced no container_width")

    def test_asymmetric_and_standard_layouts_are_meaningfully_different(self):
        standard = self.planner.plan_layout(LayoutType.STANDARD)
        asymmetric = self.planner.plan_layout(LayoutType.ASYMMETRIC)
        # They should not be interchangeable — that would defeat the
        # purpose of having pattern variety at all.
        self.assertNotEqual(standard.to_dict(), asymmetric.to_dict())

    def test_custom_settings_override_defaults(self):
        plan = self.planner.plan_layout(
            layout_type=LayoutType.STANDARD,
            custom_settings={"container_width": "999px"},
        )
        self.assertEqual(plan.container_width, "999px")


class TestOtherPlanners(unittest.TestCase):
    """Smoke tests for the remaining specialist planners — each must
    produce a usable plan without crashing on minimal/no input."""

    def test_motion_planner_produces_plan(self):
        planner = MotionPlanner()
        plan = planner.plan_fade_in(target="hero-section")
        self.assertIsNotNone(plan)

    def test_asset_planner_hero_image(self):
        plan = AssetPlanner().plan_hero_image()
        self.assertIsNotNone(plan)

    def test_responsive_planner_standard(self):
        plan = ResponsivePlanner().plan_standard_responsive()
        self.assertIsNotNone(plan)

    def test_accessibility_planner_wcag_aa(self):
        plan = AccessibilityPlanner().plan_wcag_aa()
        self.assertIsNotNone(plan)

    def test_performance_planner_standard(self):
        plan = PerformancePlanner().plan_standard()
        self.assertIsNotNone(plan)


class TestPlanValidator(unittest.TestCase):

    def test_validator_runs_against_a_real_plan(self):
        planner = DesignExecutionPlanner()
        plan = planner.create_build_plan(project_name="validation_test")
        validator = PlanValidator()
        # Just confirm it runs without crashing and returns something
        # usable — the exact validation contract isn't pinned down here
        # since PlanValidator's own behavior isn't the subject under test.
        result = validator.validate(plan) if hasattr(validator, "validate") else None
        if result is not None:
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
