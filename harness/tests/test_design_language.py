"""
Tests for harness.skills.design_resource_hub.design_language — the
consultable design-methodology reference library (ROADMAP.md FASE 3:
Design Reference Learner).

Run with: python -m unittest harness.tests.test_design_language -v
"""
import unittest

from harness.skills.design_resource_hub import (
    DesignLanguageLibrary,
    EDITORIAL_GRID_MINIMAL,
    apply_preset_to_layout_settings,
    apply_preset_to_color_hints,
    apply_preset_to_motion_settings,
)
from harness.skills.design_execution_planner import LayoutPlanner, LayoutType
from harness.skills.redesign_intelligence.color_intelligence import (
    hex_to_hsl,
    contrast_ratio,
)


class TestDesignLanguageLibrary(unittest.TestCase):

    def setUp(self):
        self.library = DesignLanguageLibrary()

    def test_default_preset_is_loaded(self):
        self.assertIsNotNone(self.library.get("editorial_grid_minimal"))

    def test_unknown_preset_returns_none(self):
        self.assertIsNone(self.library.get("does-not-exist"))

    def test_suggest_for_matches_relevant_brand_personality(self):
        matches = self.library.suggest_for(brand_personality="minimalist", visual_style="clean")
        self.assertIn(EDITORIAL_GRID_MINIMAL, matches)

    def test_suggest_for_returns_empty_when_nothing_fits(self):
        matches = self.library.suggest_for(brand_personality="loud", visual_style="maximalist-neon")
        self.assertEqual(matches, [])

    def test_custom_preset_can_be_added(self):
        from harness.skills.design_resource_hub.design_language import (
            DesignLanguagePreset, GridSystem, TypographyRules, ColorRules,
            MotionRules, ComponentRules,
        )
        custom = DesignLanguagePreset(
            id="test_preset", name="Test", description="",
            grid=GridSystem(columns=6, gutter_px_range=(8, 16), baseline_grid_px=4, spacing_base_px=4),
            typography=TypographyRules(2, (1.0, 1.1), (1.3, 1.5), (-2, -1), (2, 5), ""),
            color=ColorRules(True, True),
            motion=MotionRules(False, False, (0, 0), 1.0),
            component=ComponentRules(1, (0, 4), (5, 10), (5.0, 10.0)),
            suited_for=["brutalist"],
        )
        self.library.add(custom)
        self.assertIsNotNone(self.library.get("test_preset"))


class TestApplyToLayoutPlanner(unittest.TestCase):
    """The whole point of this library is that it actually plugs into
    the real planners — not just descriptive data nobody consumes."""

    def test_preset_produces_valid_layout_planner_settings(self):
        settings = apply_preset_to_layout_settings(EDITORIAL_GRID_MINIMAL)
        planner = LayoutPlanner()
        plan = planner.plan_layout(layout_type=LayoutType.EDITORIAL, custom_settings=settings)

        self.assertEqual(plan.columns, 12)
        self.assertEqual(plan.grid, "12-column")
        self.assertEqual(plan.white_space, "generous")


class TestApplyToColorIntelligence(unittest.TestCase):

    def test_preset_color_hints_reference_valid_hex_examples(self):
        hints = apply_preset_to_color_hints(EDITORIAL_GRID_MINIMAL)
        for hex_color in hints["neutral_reference_examples"]:
            # Must be a parseable hex color, and — matching the preset's
            # "avoid pure black/white" rule — not literally #FFFFFF or #000000.
            h, s, l = hex_to_hsl(hex_color)
            self.assertNotIn(hex_color.upper(), {"#FFFFFF", "#000000"})

    def test_preset_examples_have_low_saturation_matching_neutral_intent(self):
        hints = apply_preset_to_color_hints(EDITORIAL_GRID_MINIMAL)
        for hex_color in hints["neutral_reference_examples"]:
            _, s, _ = hex_to_hsl(hex_color)
            self.assertLess(s, 25.0, msg=f"{hex_color} is not neutral enough for a 'warm neutral' reference")

    def test_dark_mode_hints_return_dark_examples(self):
        hints = apply_preset_to_color_hints(EDITORIAL_GRID_MINIMAL, dark_mode=True)
        for hex_color in hints["neutral_reference_examples"]:
            _, _, l = hex_to_hsl(hex_color)
            self.assertLess(l, 20.0)

    def test_max_saturated_accents_is_one(self):
        hints = apply_preset_to_color_hints(EDITORIAL_GRID_MINIMAL)
        self.assertEqual(hints["max_saturated_accents"], 1)


class TestApplyToMotionSettings(unittest.TestCase):

    def test_preset_motion_settings_are_within_documented_ranges(self):
        settings = apply_preset_to_motion_settings(EDITORIAL_GRID_MINIMAL)
        low, high = EDITORIAL_GRID_MINIMAL.motion.stagger_delay_ms_range
        self.assertGreaterEqual(settings["stagger"] * 1000, low)
        self.assertLessEqual(settings["stagger"] * 1000, high)
        self.assertEqual(settings["to_state"]["scale"], 1.02)


if __name__ == "__main__":
    unittest.main(verbosity=2)
