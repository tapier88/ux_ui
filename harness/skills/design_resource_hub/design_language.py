"""
Design Language Library — real design methodology as consultable
reference data, not a template to copy.

This is the concrete implementation of ROADMAP.md FASE 3 (Design
Reference Learner): before generating a redesign, the agent should be
able to consult real, well-reasoned design methodology — grid systems,
typography rules, motion physics, component conventions — the way a
junior designer studies studio case-breakdowns before starting work.

Each DesignLanguagePreset here is built from documented design
methodology (grid theory, editorial typography conventions, spring-based
motion physics — general principles, not any single studio's literal
brand assets). The agent NEVER applies a preset wholesale as a
skin — see apply_preset_to_layout() and the module docstring in
color_intelligence.py: presets inform grid/spacing/motion/typography
*parameters*, while the actual color values always come from the
client's real BrandDNAProfile (ARCHITECTURE_PRINCIPLES.md §12). Applying
someone else's literal palette or copy would be exactly the kind of
generic reskinning this system exists to avoid.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional


@dataclass
class GridSystem:
    columns: int
    gutter_px_range: Tuple[int, int]
    baseline_grid_px: int
    spacing_base_px: int
    spacing_scale_px: List[int] = field(default_factory=lambda: [8, 16, 24, 32, 48, 64, 96])


@dataclass
class TypographyRules:
    max_font_families: int
    display_line_height_range: Tuple[float, float]
    body_line_height_range: Tuple[float, float]
    display_tracking_pct_range: Tuple[float, float]  # negative = tighter
    caps_label_tracking_pct_range: Tuple[float, float]  # positive = looser
    pairing_guidance: str


@dataclass
class ColorRules:
    prefers_warm_neutrals: bool
    avoid_pure_black_white: bool
    light_background_examples: List[str] = field(default_factory=list)
    dark_background_examples: List[str] = field(default_factory=list)
    max_saturated_accents: int = 1


@dataclass
class MotionRules:
    prefers_spring_physics: bool
    avoid_linear_easing: bool
    stagger_delay_ms_range: Tuple[int, int]
    hover_scale: float
    notes: str = ""


@dataclass
class ComponentRules:
    border_width_px: int
    border_radius_px_range: Tuple[int, int]
    shadow_blur_px_range: Tuple[int, int]
    shadow_opacity_pct_range: Tuple[float, float]


@dataclass
class DesignLanguagePreset:
    id: str
    name: str
    description: str
    grid: GridSystem
    typography: TypographyRules
    color: ColorRules
    motion: MotionRules
    component: ComponentRules
    suited_for: List[str] = field(default_factory=list)


# Derived from documented editorial-grid / Swiss-design-school
# methodology and spring-based motion conventions: strict column grids,
# baseline-aligned type, a single functional accent color against warm
# neutrals, and physics-based (not linear) motion. This is a *style of
# reasoning* about layout and motion, not a specific brand's assets.
EDITORIAL_GRID_MINIMAL = DesignLanguagePreset(
    id="editorial_grid_minimal",
    name="Editorial Grid Minimal",
    description=(
        "Strict column-grid editorial layout, warm-neutral color base with "
        "one functional accent, physics-based motion. Suited to brands "
        "that want to read as considered and premium rather than "
        "decorated — the opposite of a busy template."
    ),
    grid=GridSystem(
        columns=12,
        gutter_px_range=(16, 32),
        baseline_grid_px=8,
        spacing_base_px=8,
        spacing_scale_px=[8, 16, 24, 32, 48, 64, 96],
    ),
    typography=TypographyRules(
        max_font_families=2,
        display_line_height_range=(1.0, 1.2),
        body_line_height_range=(1.4, 1.6),
        display_tracking_pct_range=(-4.0, -2.0),
        caps_label_tracking_pct_range=(5.0, 10.0),
        pairing_guidance=(
            "One geometric/neo-grotesque sans (or a high-contrast serif) "
            "for display, one highly legible sans for body/UI — never more "
            "than two families total."
        ),
    ),
    color=ColorRules(
        prefers_warm_neutrals=True,
        avoid_pure_black_white=True,
        light_background_examples=["#FBFBF9", "#F5F5F3"],
        dark_background_examples=["#0D0D0D", "#121212"],
        max_saturated_accents=1,
    ),
    motion=MotionRules(
        prefers_spring_physics=True,
        avoid_linear_easing=True,
        stagger_delay_ms_range=(50, 100),
        hover_scale=1.02,
        notes=(
            "High stiffness for a fast start, balanced damping so elements "
            "settle without oscillating — overshoot reads as unpolished."
        ),
    ),
    component=ComponentRules(
        border_width_px=1,
        border_radius_px_range=(6, 12),
        shadow_blur_px_range=(20, 40),
        shadow_opacity_pct_range=(2.0, 3.0),
    ),
    suited_for=["minimalist", "editorial", "professional", "tech", "premium", "portfolio"],
)


class DesignLanguageLibrary:
    """Registry of consultable design-language presets."""

    def __init__(self):
        self._presets: Dict[str, DesignLanguagePreset] = {}
        self._load_defaults()

    def _load_defaults(self):
        self.add(EDITORIAL_GRID_MINIMAL)

    def add(self, preset: DesignLanguagePreset):
        self._presets[preset.id] = preset

    def get(self, preset_id: str) -> Optional[DesignLanguagePreset]:
        return self._presets.get(preset_id)

    def all(self) -> List[DesignLanguagePreset]:
        return list(self._presets.values())

    def suggest_for(self, brand_personality: str, visual_style: str) -> List[DesignLanguagePreset]:
        """Return presets whose suited_for tags match the brand's
        personality/visual style — not a forced default, a candidate
        list for Redesign Intelligence to weigh against the real
        BrandDNAProfile."""
        needle = f"{brand_personality} {visual_style}".lower()
        return [p for p in self._presets.values() if any(tag in needle for tag in p.suited_for)]


def apply_preset_to_layout_settings(preset: DesignLanguagePreset) -> Dict:
    """Translate a preset's grid rules into LayoutPlanner-compatible
    custom_settings (see design_execution_planner.LayoutPlan fields)."""
    gutter_px = sum(preset.grid.gutter_px_range) // 2
    return {
        "columns": preset.grid.columns,
        "grid": f"{preset.grid.columns}-column",
        "gaps": {"row": f"{gutter_px}px", "col": f"{gutter_px}px"},
        "white_space": "generous",
    }


def apply_preset_to_color_hints(preset: DesignLanguagePreset, dark_mode: bool = False) -> Dict:
    """Translate a preset's color rules into hints for PaletteGenerator
    (color_intelligence.py) — hints only, never literal brand colors.
    The client's real primary brand color always drives generate();
    this only informs neutral tone and accent-count discipline."""
    examples = preset.color.dark_background_examples if dark_mode else preset.color.light_background_examples
    return {
        "prefers_warm_neutrals": preset.color.prefers_warm_neutrals,
        "neutral_reference_examples": examples,
        "max_saturated_accents": preset.color.max_saturated_accents,
    }


def apply_preset_to_motion_settings(preset: DesignLanguagePreset) -> Dict:
    """Translate a preset's motion rules into MotionPlanner-compatible
    parameters (see design_execution_planner.motion_planner)."""
    stagger_ms = sum(preset.motion.stagger_delay_ms_range) // 2
    return {
        "stagger": stagger_ms / 1000.0,
        "easing": "spring" if preset.motion.prefers_spring_physics else "cubic-bezier(0.4, 0, 0.2, 1)",
        "to_state": {"scale": preset.motion.hover_scale},
    }
