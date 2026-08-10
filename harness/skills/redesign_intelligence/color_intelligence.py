"""
Color Intelligence — real color theory, not generic AI palettes.

Replaces the previous behavior of ColorStrategyEngine (see engine.py),
which only echoed back whatever colors were already in the profile and
suggested "define a primary color" in plain text when they were missing.
That produces either nothing, or whatever a template already had —
never an actual palette grounded in color theory and the client's real
brand color.

Core idea (ARCHITECTURE_PRINCIPLES.md §12 applied to color): the agent
never invents a palette from a generic "AI purple-to-blue gradient." It
takes the ACTUAL brand color extracted from the client's site and builds
outward from it using real color theory — harmony rules, a proper
tint/shade ramp, brand-tinted neutrals, and WCAG-verified pairings — so
the result still reads as "this brand, elevated," not "a template with
their logo pasted on it." See DESIGN_METHODOLOGY.md for the full flow
this plugs into.

Pure stdlib (colorsys) — no design/graphics dependencies required.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import colorsys
import re


HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")

# WCAG 2.1 AA minimum contrast ratio for normal-size text.
WCAG_AA_NORMAL_TEXT = 4.5

# Fixed semantic hue anchors (standard UI convention: green=success,
# amber=warning, red=error, blue=info). These are ANCHORS, not final
# colors — generate_semantic_colors() re-tunes their saturation and
# lightness to match the brand's character so they harmonize instead of
# looking like they were pasted in from a generic UI kit.
SEMANTIC_HUE_ANCHORS = {
    "success": 142.0,
    "warning": 38.0,
    "error": 4.0,
    "info": 217.0,
}


def normalize_hex(hex_color: str) -> str:
    match = HEX_RE.match(hex_color.strip())
    if not match:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    return f"#{match.group(1).upper()}"


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = normalize_hex(hex_color)
    return (
        int(hex_color[1:3], 16),
        int(hex_color[3:5], 16),
        int(hex_color[5:7], 16),
    )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    r, g, b = (max(0, min(255, round(v))) for v in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    """Returns (hue 0-360, saturation 0-100, lightness 0-100)."""
    r, g, b = hex_to_rgb(hex_color)
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    return (h * 360.0, s * 100.0, l * 100.0)


def hsl_to_hex(h: float, s: float, l: float) -> str:
    h = h % 360.0
    s = max(0.0, min(100.0, s)) / 100.0
    l = max(0.0, min(100.0, l)) / 100.0
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return rgb_to_hex(r * 255, g * 255, b * 255)


def relative_luminance(hex_color: str) -> float:
    """WCAG 2.1 relative luminance formula."""
    r, g, b = (v / 255.0 for v in hex_to_rgb(hex_color))

    def _linearize(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _linearize(r), _linearize(g), _linearize(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG 2.1 contrast ratio between two colors (1.0 to 21.0)."""
    l1 = relative_luminance(hex_a) + 0.05
    l2 = relative_luminance(hex_b) + 0.05
    return round(max(l1, l2) / min(l1, l2), 2)


def best_text_color(background_hex: str) -> str:
    """Pick whichever of near-black/near-white has higher contrast
    against the given background — the standard accessible-text-color
    heuristic, computed rather than guessed."""
    near_black = "#0A0A0A"
    near_white = "#FAFAFA"
    return near_black if contrast_ratio(background_hex, near_black) >= contrast_ratio(background_hex, near_white) \
        else near_white


def ensure_contrast(
    foreground_hex: str,
    background_hex: str,
    minimum: float = WCAG_AA_NORMAL_TEXT,
    max_steps: int = 20,
) -> Tuple[str, bool]:
    """If foreground/background don't meet the minimum contrast ratio,
    push the foreground's lightness away from the background's until
    they do (or until max_steps is exhausted). Returns (adjusted_hex,
    was_adjusted).

    This is what makes the generator "genius" rather than just
    decorative: it doesn't hand back a palette with a broken contrast
    pair and a hopeful note — it actively fixes it, the same way a
    careful designer would nudge a color until it reads properly.
    """
    if contrast_ratio(foreground_hex, background_hex) >= minimum:
        return foreground_hex, False

    h, s, l = hex_to_hsl(foreground_hex)
    _, _, bg_l = hex_to_hsl(background_hex)
    direction = -1.0 if bg_l >= 50.0 else 1.0  # darken fg on light bg, lighten on dark bg

    for step in range(1, max_steps + 1):
        candidate_l = max(0.0, min(100.0, l + direction * step * (100.0 / max_steps)))
        candidate = hsl_to_hex(h, s, candidate_l)
        if contrast_ratio(candidate, background_hex) >= minimum:
            return candidate, True

    # Fall back to guaranteed-safe pure black/white if the hue simply
    # can't reach the target ratio at any lightness.
    return best_text_color(background_hex), True


# --- Harmony generation -----------------------------------------------

def complementary(hex_color: str) -> str:
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h + 180, s, l)


def analogous(hex_color: str, angle: float = 30.0) -> Tuple[str, str]:
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h - angle, s, l), hsl_to_hex(h + angle, s, l)


def triadic(hex_color: str) -> Tuple[str, str]:
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h + 120, s, l), hsl_to_hex(h + 240, s, l)


def split_complementary(hex_color: str, angle: float = 30.0) -> Tuple[str, str]:
    h, s, l = hex_to_hsl(hex_color)
    return hsl_to_hex(h + 180 - angle, s, l), hsl_to_hex(h + 180 + angle, s, l)


# --- Tint/shade ramp -----------------------------------------------

# Lightness targets mirroring the familiar 50-900 design-token scale
# (Tailwind/Material-style), but computed from the brand's own hue and
# saturation instead of a generic pre-baked ramp.
RAMP_LIGHTNESS_TARGETS = {
    50: 97, 100: 93, 200: 85, 300: 75, 400: 65,
    500: 50, 600: 42, 700: 34, 800: 26, 900: 16,
}


def generate_ramp(hex_color: str) -> Dict[int, str]:
    """Generate a full tint/shade ramp from a single brand color.

    Saturation is gently reduced at the extremes (very light/very dark
    steps) — pushing full saturation to L=97 or L=16 tends to produce
    muddy or neon-looking results; real design systems taper it.
    """
    h, s, _ = hex_to_hsl(hex_color)
    ramp: Dict[int, str] = {}
    for step, target_l in RAMP_LIGHTNESS_TARGETS.items():
        distance_from_mid = abs(target_l - 50) / 50.0  # 0 at L=50, 1 at extremes
        tapered_s = s * (1.0 - 0.35 * distance_from_mid)
        ramp[step] = hsl_to_hex(h, tapered_s, target_l)
    return ramp


# --- Full palette generation -----------------------------------------------

@dataclass
class GeneratedPalette:
    primary: str
    secondary: str
    accent: str
    background: str
    foreground: str
    muted: str
    primary_ramp: Dict[int, str] = field(default_factory=dict)
    semantic_colors: Dict[str, str] = field(default_factory=dict)
    contrast_report: Dict[str, float] = field(default_factory=dict)
    harmony_used: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "foreground": self.foreground,
            "muted": self.muted,
            "primary_ramp": self.primary_ramp,
            "semantic_colors": self.semantic_colors,
            "contrast_report": self.contrast_report,
            "harmony_used": self.harmony_used,
            "notes": self.notes,
        }

    def accessibility_score(self) -> float:
        """0-100 score for the ElevationScorer 'accessibility' signal
        contribution attributable to color choices: the fraction of
        checked pairs that meet WCAG AA."""
        if not self.contrast_report:
            return 0.0
        passing = sum(1 for ratio in self.contrast_report.values() if ratio >= WCAG_AA_NORMAL_TEXT)
        return round(100.0 * passing / len(self.contrast_report), 2)


class PaletteGenerator:
    """Builds a complete, accessible, brand-anchored palette from one or
    two real brand colors — see module docstring for the design
    philosophy (§12: build outward from real brand data, not from a
    generic template)."""

    def generate(
        self,
        brand_primary_hex: str,
        brand_secondary_hex: Optional[str] = None,
        dark_mode: bool = False,
    ) -> GeneratedPalette:
        primary = normalize_hex(brand_primary_hex)
        h, s, l = hex_to_hsl(primary)
        notes: List[str] = []

        # Very low-saturation brand colors (near-grayscale, e.g. a lot of
        # premium/editorial brands) should NOT have an artificial harmony
        # forced onto them — that's exactly the kind of "AI palette"
        # over-decoration that makes minimalist brands look cheap.
        near_neutral_brand = s < 12.0

        if brand_secondary_hex:
            secondary = normalize_hex(brand_secondary_hex)
            harmony_used = "brand-provided secondary"
            accent = complementary(primary) if not near_neutral_brand else hsl_to_hex(h, min(s + 20, 60), 50)
        elif near_neutral_brand:
            secondary = hsl_to_hex(h, s, max(0.0, l - 20))
            accent = hsl_to_hex(h, min(s + 15, 40), 50)
            harmony_used = "monochrome (brand color is near-neutral)"
            notes.append(
                "Brand primary has low saturation — used a monochrome/tonal "
                "strategy instead of forcing an artificial complementary "
                "harmony, to keep the minimalist brand character intact."
            )
        else:
            # Split-complementary reads as considered and sophisticated;
            # plain complementary tends toward the garish, high-contrast
            # look that's a giveaway of generic template design.
            sc1, sc2 = split_complementary(primary)
            secondary = sc1
            accent = sc2
            harmony_used = "split-complementary"

        if dark_mode:
            background = hsl_to_hex(h, min(s, 15), 8)
            foreground = hsl_to_hex(h, min(s, 8), 95)
        else:
            # Neutrals subtly tinted with the brand hue, not pure
            # #FFFFFF/#000000 — a small, deliberate touch that reads as
            # "designed" rather than "default".
            background = hsl_to_hex(h, min(s, 8), 98)
            foreground = hsl_to_hex(h, min(s, 15), 11)

        muted = hsl_to_hex(h, s * 0.3, 45)

        foreground, fg_adjusted = ensure_contrast(foreground, background)
        if fg_adjusted:
            notes.append("Foreground lightness adjusted to meet WCAG AA against background.")

        primary_on_bg, primary_adjusted = ensure_contrast(primary, background, minimum=3.0)
        # 3.0 is the WCAG AA threshold for large text / UI components,
        # not overwritten in place — primary stays the true brand color;
        # this only informs whether it's safe to use for body text.
        if primary_adjusted:
            notes.append(
                "Brand primary color does not meet AA contrast for text use "
                "against the generated background — reserve it for large "
                "text, icons, or fills, and use the primary_ramp's darker "
                "steps for small text instead."
            )

        semantic_colors = generate_semantic_colors(h, s)

        contrast_report = {
            "foreground_on_background": contrast_ratio(foreground, background),
            "primary_on_background": contrast_ratio(primary, background),
            "secondary_on_background": contrast_ratio(secondary, background),
            "accent_on_background": contrast_ratio(accent, background),
        }

        return GeneratedPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            foreground=foreground,
            muted=muted,
            primary_ramp=generate_ramp(primary),
            semantic_colors=semantic_colors,
            contrast_report=contrast_report,
            harmony_used=harmony_used,
            notes=notes,
        )


def generate_semantic_colors(brand_hue: float, brand_saturation: float) -> Dict[str, str]:
    """Success/warning/error/info tuned to the brand's saturation
    character so they harmonize with the rest of the palette instead of
    looking like they were dropped in from an unrelated UI kit."""
    # Clamp: semantic colors still need to read clearly as their role,
    # so we don't fully adopt a very low brand saturation — just move
    # partway toward it from a reasonably vivid baseline.
    target_saturation = max(45.0, min(75.0, brand_saturation * 0.6 + 45.0 * 0.4))
    return {
        role: hsl_to_hex(hue, target_saturation, 45.0)
        for role, hue in SEMANTIC_HUE_ANCHORS.items()
    }
