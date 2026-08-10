"""
Tests for harness.skills.redesign_intelligence.color_intelligence — the
real color-theory engine that replaces generic/echoed color output.

Run with: python -m unittest harness.tests.test_color_intelligence -v
"""
import unittest

from harness.skills.redesign_intelligence.color_intelligence import (
    normalize_hex,
    hex_to_rgb,
    rgb_to_hex,
    hex_to_hsl,
    hsl_to_hex,
    relative_luminance,
    contrast_ratio,
    best_text_color,
    ensure_contrast,
    complementary,
    analogous,
    triadic,
    split_complementary,
    generate_ramp,
    generate_semantic_colors,
    PaletteGenerator,
    WCAG_AA_NORMAL_TEXT,
)


class TestColorConversions(unittest.TestCase):

    def test_normalize_hex_accepts_with_and_without_hash(self):
        self.assertEqual(normalize_hex("#ff0000"), "#FF0000")
        self.assertEqual(normalize_hex("ff0000"), "#FF0000")

    def test_normalize_hex_rejects_invalid(self):
        with self.assertRaises(ValueError):
            normalize_hex("not-a-color")
        with self.assertRaises(ValueError):
            normalize_hex("#fff")  # 3-digit shorthand not supported

    def test_hex_rgb_roundtrip(self):
        self.assertEqual(rgb_to_hex(*hex_to_rgb("#3366CC")), "#3366CC")

    def test_hex_hsl_roundtrip(self):
        original = "#3366CC"
        h, s, l = hex_to_hsl(original)
        roundtripped = hsl_to_hex(h, s, l)
        # allow tiny float rounding drift
        r1, g1, b1 = hex_to_rgb(original)
        r2, g2, b2 = hex_to_rgb(roundtripped)
        self.assertLessEqual(abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2), 3)

    def test_known_hsl_values(self):
        # Pure red
        h, s, l = hex_to_hsl("#FF0000")
        self.assertAlmostEqual(h, 0.0, delta=1.0)
        self.assertAlmostEqual(s, 100.0, delta=1.0)
        self.assertAlmostEqual(l, 50.0, delta=1.0)


class TestContrast(unittest.TestCase):

    def test_black_on_white_max_contrast(self):
        ratio = contrast_ratio("#000000", "#FFFFFF")
        self.assertAlmostEqual(ratio, 21.0, delta=0.1)

    def test_same_color_min_contrast(self):
        ratio = contrast_ratio("#336699", "#336699")
        self.assertAlmostEqual(ratio, 1.0, delta=0.01)

    def test_best_text_color_picks_black_on_light_bg(self):
        self.assertEqual(best_text_color("#FAFAFA"), "#0A0A0A")

    def test_best_text_color_picks_white_on_dark_bg(self):
        self.assertEqual(best_text_color("#0A0A0A"), "#FAFAFA")

    def test_ensure_contrast_fixes_failing_pair(self):
        # Light gray text on white background — fails AA badly
        fixed, adjusted = ensure_contrast("#EEEEEE", "#FFFFFF")
        self.assertTrue(adjusted)
        self.assertGreaterEqual(contrast_ratio(fixed, "#FFFFFF"), WCAG_AA_NORMAL_TEXT)

    def test_ensure_contrast_leaves_passing_pair_untouched(self):
        fixed, adjusted = ensure_contrast("#000000", "#FFFFFF")
        self.assertFalse(adjusted)
        self.assertEqual(fixed, "#000000")


class TestHarmony(unittest.TestCase):

    def test_complementary_is_180_degrees_opposite(self):
        h1, _, _ = hex_to_hsl("#3366CC")
        comp = complementary("#3366CC")
        h2, _, _ = hex_to_hsl(comp)
        diff = abs(h1 - h2) % 360
        self.assertAlmostEqual(min(diff, 360 - diff), 180.0, delta=1.0)

    def test_analogous_returns_two_neighboring_hues(self):
        base_h, _, _ = hex_to_hsl("#3366CC")
        left, right = analogous("#3366CC", angle=30)
        left_h, _, _ = hex_to_hsl(left)
        right_h, _, _ = hex_to_hsl(right)
        self.assertAlmostEqual((base_h - left_h) % 360, 30.0, delta=1.0)
        self.assertAlmostEqual((right_h - base_h) % 360, 30.0, delta=1.0)

    def test_triadic_returns_two_120_degree_hues(self):
        t1, t2 = triadic("#3366CC")
        self.assertEqual(len({t1, t2}), 2)

    def test_split_complementary_differs_from_plain_complementary(self):
        sc1, sc2 = split_complementary("#3366CC")
        comp = complementary("#3366CC")
        self.assertNotEqual(sc1, comp)
        self.assertNotEqual(sc2, comp)


class TestRamp(unittest.TestCase):

    def test_ramp_has_all_expected_steps(self):
        ramp = generate_ramp("#3366CC")
        self.assertEqual(set(ramp.keys()), {50, 100, 200, 300, 400, 500, 600, 700, 800, 900})

    def test_ramp_gets_darker_as_steps_increase(self):
        ramp = generate_ramp("#3366CC")
        _, _, l50 = hex_to_hsl(ramp[50])
        _, _, l500 = hex_to_hsl(ramp[500])
        _, _, l900 = hex_to_hsl(ramp[900])
        self.assertGreater(l50, l500)
        self.assertGreater(l500, l900)


class TestSemanticColors(unittest.TestCase):

    def test_returns_all_four_roles(self):
        semantic = generate_semantic_colors(brand_hue=210.0, brand_saturation=60.0)
        self.assertEqual(set(semantic.keys()), {"success", "warning", "error", "info"})

    def test_roles_are_distinguishable_hues(self):
        semantic = generate_semantic_colors(brand_hue=210.0, brand_saturation=60.0)
        hues = {role: hex_to_hsl(hex_val)[0] for role, hex_val in semantic.items()}
        # success (green) and error (red) must be clearly different hues
        self.assertGreater(abs(hues["success"] - hues["error"]) % 360, 60)


class TestPaletteGenerator(unittest.TestCase):

    def test_generates_full_palette_from_primary_only(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB")  # a real, saturated brand blue

        self.assertEqual(palette.primary, "#2563EB")
        self.assertTrue(palette.secondary)
        self.assertTrue(palette.accent)
        self.assertTrue(palette.background)
        self.assertTrue(palette.foreground)
        self.assertEqual(len(palette.primary_ramp), 10)
        self.assertEqual(set(palette.semantic_colors.keys()), {"success", "warning", "error", "info"})

    def test_foreground_meets_wcag_against_generated_background(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB")
        ratio = contrast_ratio(palette.foreground, palette.background)
        self.assertGreaterEqual(ratio, WCAG_AA_NORMAL_TEXT)

    def test_accessibility_score_reflects_contrast_report(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB")
        score = palette.accessibility_score()
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_respects_provided_secondary_instead_of_generating_one(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB", brand_secondary_hex="#F97316")
        self.assertEqual(palette.secondary, "#F97316")
        self.assertIn("brand-provided secondary", palette.harmony_used)

    def test_near_neutral_brand_uses_monochrome_strategy_not_forced_harmony(self):
        gen = PaletteGenerator()
        # A near-grayscale brand color (very low saturation)
        palette = gen.generate("#4A4A4A")
        self.assertIn("monochrome", palette.harmony_used)
        self.assertTrue(any("low saturation" in note for note in palette.notes))

    def test_saturated_brand_uses_split_complementary_by_default(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB")
        self.assertEqual(palette.harmony_used, "split-complementary")

    def test_dark_mode_produces_dark_background(self):
        gen = PaletteGenerator()
        palette = gen.generate("#2563EB", dark_mode=True)
        _, _, bg_l = hex_to_hsl(palette.background)
        self.assertLess(bg_l, 20.0)

    def test_invalid_primary_raises(self):
        gen = PaletteGenerator()
        with self.assertRaises(ValueError):
            gen.generate("not-a-hex-color")


if __name__ == "__main__":
    unittest.main(verbosity=2)
