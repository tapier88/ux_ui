"""
Design Execution Planner - Models
Core data models for design build planning
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class LayoutType(Enum):
    """Layout types for sections"""
    ASYMMETRIC = "asymmetric"
    EDITORIAL = "editorial"
    OVERLAPPING = "overlapping"
    IMMERSIVE = "immersive"
    BENTO = "bento"
    FULL_BLEED = "full_bleed"
    LAYERED = "layered"
    DIAGONAL = "diagonal"
    STORYTELLING = "storytelling"
    EXPERIMENTAL = "experimental"
    SPLIT = "split"
    CENTERED = "centered"
    GRID = "grid"
    HORIZONTAL = "horizontal"
    STICKY = "sticky"
    STANDARD = "standard"


class AnimationType(Enum):
    """Animation types"""
    FADE = "fade"
    SLIDE = "slide"
    SCALE = "scale"
    REVEAL = "reveal"
    PARALLAX = "parallax"
    STICKY = "sticky"
    PIN = "pin"
    SCRUB = "scrub"
    STAGGER = "stagger"
    HORIZONTAL = "horizontal"
    TRANSFORM = "transform"


class AssetType(Enum):
    """Asset types"""
    IMAGE = "image"
    ILLUSTRATION = "illustration"
    ICON = "icon"
    VIDEO = "video"
    THREE_D = "3d"
    BACKGROUND = "background"
    TEXTURE = "texture"
    LOGO = "logo"


class ResourceSource(Enum):
    """Resource sources"""
    REACT_BITS = "react-bits"
    SHADCN = "shadcn"
    MOTION = "motion"
    GSAP = "gsap"
    LENIS = "lenis"
    TAILWIND = "tailwind"
    CUSTOM = "custom"
    NONE = "none"


class CodeAction(Enum):
    """Actions for existing code"""
    PRESERVE = "preserve"
    MODIFY = "modify"
    REPLACE = "replace"
    CREATE = "create"
    REMOVE = "remove"


class ResponsiveBreakpoint(Enum):
    """Responsive breakpoints"""
    DESKTOP = "desktop"
    TABLET = "tablet"
    MOBILE = "mobile"


# =============================================================================
# DESIGN TOKENS
# =============================================================================

@dataclass
class ColorTokens:
    """Color design tokens"""
    primary: str = "#000000"
    secondary: str = "#666666"
    accent: str = "#3B82F6"
    background: str = "#FFFFFF"
    surface: str = "#F8F9FA"
    text: str = "#1A1A1A"
    muted: str = "#6B7280"
    border: str = "#E5E7EB"
    success: str = "#10B981"
    warning: str = "#F59E0B"
    error: str = "#EF4444"


@dataclass
class TypographyTokens:
    """Typography design tokens"""
    font_family: str = "Inter, system-ui, sans-serif"
    heading_font: str = "Inter, system-ui, sans-serif"
    body_font: str = "Inter, system-ui, sans-serif"
    display_scale: float = 1.25
    h1: Dict[str, Any] = field(default_factory=lambda: {"size": "3rem", "weight": "700", "line_height": "1.1"})
    h2: Dict[str, Any] = field(default_factory=lambda: {"size": "2.25rem", "weight": "600", "line_height": "1.2"})
    h3: Dict[str, Any] = field(default_factory=lambda: {"size": "1.5rem", "weight": "600", "line_height": "1.3"})
    body: Dict[str, Any] = field(default_factory=lambda: {"size": "1rem", "weight": "400", "line_height": "1.6"})
    small: Dict[str, Any] = field(default_factory=lambda: {"size": "0.875rem", "weight": "400", "line_height": "1.5"})
    letter_spacing: str = "normal"
    max_width: str = "65ch"
    text_alignment: str = "left"


@dataclass
class SpacingTokens:
    """Spacing design tokens"""
    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"
    xxxl: str = "4rem"


@dataclass
class RadiusTokens:
    """Border radius tokens"""
    none: str = "0"
    sm: str = "0.25rem"
    md: str = "0.5rem"
    lg: str = "0.75rem"
    xl: str = "1rem"
    full: str = "9999px"


@dataclass
class ShadowTokens:
    """Shadow tokens"""
    none: str = "none"
    sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    md: str = "0 4px 6px rgba(0,0,0,0.1)"
    lg: str = "0 10px 15px rgba(0,0,0,0.1)"
    xl: str = "0 20px 25px rgba(0,0,0,0.15)"
    inner: str = "inset 0 2px 4px rgba(0,0,0,0.06)"


@dataclass
class BorderTokens:
    """Border tokens"""
    none: str = "none"
    sm: str = "1px solid"
    md: str = "2px solid"
    lg: str = "4px solid"


@dataclass
class BreakpointTokens:
    """Breakpoint tokens"""
    mobile: str = "640px"
    tablet: str = "768px"
    desktop: str = "1024px"
    wide: str = "1280px"


@dataclass
class MotionTokens:
    """Motion tokens"""
    duration_fast: str = "150ms"
    duration_normal: str = "300ms"
    duration_slow: str = "500ms"
    easing_linear: str = "linear"
    easing_ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    easing_ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    easing_ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"


@dataclass
class ZIndexTokens:
    """Z-index tokens"""
    base: int = 0
    dropdown: int = 1000
    sticky: int = 1100
    fixed: int = 1200
    modal_backdrop: int = 1300
    modal: int = 1400
    popover: int = 1500
    tooltip: int = 1600


@dataclass
class DesignTokens:
    """Complete design token set"""
    colors: ColorTokens = field(default_factory=ColorTokens)
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)
    radii: RadiusTokens = field(default_factory=RadiusTokens)
    shadows: ShadowTokens = field(default_factory=ShadowTokens)
    borders: BorderTokens = field(default_factory=BorderTokens)
    breakpoints: BreakpointTokens = field(default_factory=BreakpointTokens)
    motion: MotionTokens = field(default_factory=MotionTokens)
    z_index: ZIndexTokens = field(default_factory=ZIndexTokens)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "colors": {k: v for k, v in self.colors.__dict__.items()},
            "typography": {k: v for k, v in self.typography.__dict__.items()},
            "spacing": {k: v for k, v in self.spacing.__dict__.items()},
            "radii": {k: v for k, v in self.radii.__dict__.items()},
            "shadows": {k: v for k, v in self.shadows.__dict__.items()},
            "borders": {k: v for k, v in self.borders.__dict__.items()},
            "breakpoints": {k: v for k, v in self.breakpoints.__dict__.items()},
            "motion": {k: v for k, v in self.motion.__dict__.items()},
            "z_index": {k: v for k, v in self.z_index.__dict__.items()}
        }


# =============================================================================
# PAGE PLANNING
# =============================================================================

@dataclass
class PagePlan:
    """Page architecture plan"""
    route: str
    purpose: str
    sections: List[str] = field(default_factory=list)
    primary_cta: Optional[str] = None
    secondary_cta: Optional[str] = None
    navigation: Optional[str] = None
    footer: Optional[str] = None
    seo_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route,
            "purpose": self.purpose,
            "sections": self.sections,
            "primary_cta": self.primary_cta,
            "secondary_cta": self.secondary_cta,
            "navigation": self.navigation,
            "footer": self.footer,
            "seo_requirements": self.seo_requirements
        }


# =============================================================================
# SECTION PLANNING
# =============================================================================

@dataclass
class SectionPlan:
    """Section plan"""
    id: str
    name: str
    purpose: str
    layout: LayoutType = LayoutType.STANDARD
    content: Dict[str, Any] = field(default_factory=dict)
    components: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    background: Dict[str, Any] = field(default_factory=dict)
    typography: Dict[str, Any] = field(default_factory=dict)
    motion: List[str] = field(default_factory=list)
    responsive_behavior: Dict[str, Any] = field(default_factory=dict)
    accessibility: Dict[str, Any] = field(default_factory=dict)
    performance_priority: str = "normal"  # low, normal, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "layout": self.layout.value,
            "content": self.content,
            "components": self.components,
            "assets": self.assets,
            "background": self.background,
            "typography": self.typography,
            "motion": self.motion,
            "responsive_behavior": self.responsive_behavior,
            "accessibility": self.accessibility,
            "performance_priority": self.performance_priority
        }


# =============================================================================
# COMPONENT PLANNING
# =============================================================================

@dataclass
class ComponentPlan:
    """Component plan"""
    id: str
    name: str
    type: str
    purpose: str
    source_resource: ResourceSource = ResourceSource.CUSTOM
    variants: List[str] = field(default_factory=list)
    props: Dict[str, Any] = field(default_factory=dict)
    states: List[str] = field(default_factory=list)
    responsive_behavior: Dict[str, Any] = field(default_factory=dict)
    accessibility: Dict[str, Any] = field(default_factory=dict)
    animation: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    inspiration_source: Optional[str] = None
    adaptation_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "purpose": self.purpose,
            "source_resource": self.source_resource.value,
            "variants": self.variants,
            "props": self.props,
            "states": self.states,
            "responsive_behavior": self.responsive_behavior,
            "accessibility": self.accessibility,
            "animation": self.animation,
            "dependencies": self.dependencies,
            "inspiration_source": self.inspiration_source,
            "adaptation_reason": self.adaptation_reason
        }


# =============================================================================
# LAYOUT PLANNING
# =============================================================================

@dataclass
class LayoutPlan:
    """Layout plan"""
    container_width: str = "1200px"
    grid: str = "12-column"
    columns: int = 12
    gaps: Dict[str, str] = field(default_factory=lambda: {"row": "1.5rem", "col": "1.5rem"})
    alignment: str = "center"
    positioning: str = "relative"
    layering: List[str] = field(default_factory=list)
    overlap: bool = False
    z_index: Dict[str, int] = field(default_factory=dict)
    image_position: str = "right"
    text_position: str = "left"
    content_density: str = "normal"  # sparse, normal, dense
    white_space: str = "generous"  # minimal, normal, generous
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "container_width": self.container_width,
            "grid": self.grid,
            "columns": self.columns,
            "gaps": self.gaps,
            "alignment": self.alignment,
            "positioning": self.positioning,
            "layering": self.layering,
            "overlap": self.overlap,
            "z_index": self.z_index,
            "image_position": self.image_position,
            "text_position": self.text_position,
            "content_density": self.content_density,
            "white_space": self.white_space
        }


# =============================================================================
# ASSET PLANNING
# =============================================================================

@dataclass
class GenerationRequest:
    """Asset generation request for Higgsfield"""
    asset_type: str
    creative_direction: str
    composition: str
    style: str
    aspect_ratio: str
    resolution: str
    purpose: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_type": self.asset_type,
            "creative_direction": self.creative_direction,
            "composition": self.composition,
            "style": self.style,
            "aspect_ratio": self.aspect_ratio,
            "resolution": self.resolution,
            "purpose": self.purpose
        }


@dataclass
class AssetPlan:
    """Asset plan"""
    id: str
    type: AssetType
    purpose: str
    source: Optional[str] = None
    generation_required: bool = False
    generator: Optional[str] = None
    dimensions: Optional[Dict[str, int]] = None
    aspect_ratio: Optional[str] = None
    format: str = "webp"
    priority: str = "normal"  # low, normal, high, critical
    optimization: Dict[str, Any] = field(default_factory=dict)
    generation_request: Optional[GenerationRequest] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "type": self.type.value,
            "purpose": self.purpose,
            "source": self.source,
            "generation_required": self.generation_required,
            "generator": self.generator,
            "dimensions": self.dimensions,
            "aspect_ratio": self.aspect_ratio,
            "format": self.format,
            "priority": self.priority,
            "optimization": self.optimization
        }
        if self.generation_request:
            result["generation_request"] = self.generation_request.to_dict()
        return result


# =============================================================================
# MOTION PLANNING
# =============================================================================

@dataclass
class MotionPlan:
    """Motion/animation plan"""
    target: str
    trigger: str
    type: AnimationType
    duration: str = "300ms"
    delay: str = "0ms"
    easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    from_state: Dict[str, Any] = field(default_factory=dict)
    to_state: Dict[str, Any] = field(default_factory=dict)
    scrub: bool = False
    pin: bool = False
    stagger: Optional[float] = None
    priority: str = "normal"
    mobile_behavior: Optional[str] = None
    reduced_motion_behavior: Optional[str] = None
    resource: ResourceSource = ResourceSource.MOTION
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "trigger": self.trigger,
            "type": self.type.value,
            "duration": self.duration,
            "delay": self.delay,
            "easing": self.easing,
            "from": self.from_state,
            "to": self.to_state,
            "scrub": self.scrub,
            "pin": self.pin,
            "stagger": self.stagger,
            "priority": self.priority,
            "mobile_behavior": self.mobile_behavior,
            "reduced_motion_behavior": self.reduced_motion_behavior,
            "resource": self.resource.value
        }


# =============================================================================
# RESPONSIVE PLANNING
# =============================================================================

@dataclass
class ResponsiveBehavior:
    """Responsive behavior for a breakpoint"""
    layout_change: Optional[str] = None
    font_change: Optional[Dict[str, Any]] = None
    spacing_change: Optional[Dict[str, Any]] = None
    image_change: Optional[Dict[str, Any]] = None
    animation_change: Optional[str] = None
    visibility_change: bool = False
    interaction_change: Optional[str] = None


@dataclass
class ResponsivePlan:
    """Responsive plan"""
    desktop: ResponsiveBehavior = field(default_factory=ResponsiveBehavior)
    tablet: ResponsiveBehavior = field(default_factory=ResponsiveBehavior)
    mobile: ResponsiveBehavior = field(default_factory=ResponsiveBehavior)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "desktop": {
                "layout_change": self.desktop.layout_change,
                "font_change": self.desktop.font_change,
                "spacing_change": self.desktop.spacing_change,
                "image_change": self.desktop.image_change,
                "animation_change": self.desktop.animation_change,
                "visibility_change": self.desktop.visibility_change,
                "interaction_change": self.desktop.interaction_change
            },
            "tablet": {
                "layout_change": self.tablet.layout_change,
                "font_change": self.tablet.font_change,
                "spacing_change": self.tablet.spacing_change,
                "image_change": self.tablet.image_change,
                "animation_change": self.tablet.animation_change,
                "visibility_change": self.tablet.visibility_change,
                "interaction_change": self.tablet.interaction_change
            },
            "mobile": {
                "layout_change": self.mobile.layout_change,
                "font_change": self.mobile.font_change,
                "spacing_change": self.mobile.spacing_change,
                "image_change": self.mobile.image_change,
                "animation_change": self.mobile.animation_change,
                "visibility_change": self.mobile.visibility_change,
                "interaction_change": self.mobile.interaction_change
            }
        }


# =============================================================================
# ACCESSIBILITY PLANNING
# =============================================================================

@dataclass
class AccessibilityPlan:
    """Accessibility plan"""
    semantic_html: bool = True
    keyboard_navigation: bool = True
    focus_states: Dict[str, Any] = field(default_factory=lambda: {"outline": "2px solid", "offset": "2px"})
    aria: Dict[str, Any] = field(default_factory=dict)
    contrast: Dict[str, Any] = field(default_factory=lambda: {"min_ratio": 4.5, "large_text_ratio": 3})
    reduced_motion: bool = True
    screen_reader: Dict[str, Any] = field(default_factory=dict)
    touch_targets: Dict[str, Any] = field(default_factory=lambda: {"min_size": "44px"})
    form_accessibility: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "semantic_html": self.semantic_html,
            "keyboard_navigation": self.keyboard_navigation,
            "focus_states": self.focus_states,
            "aria": self.aria,
            "contrast": self.contrast,
            "reduced_motion": self.reduced_motion,
            "screen_reader": self.screen_reader,
            "touch_targets": self.touch_targets,
            "form_accessibility": self.form_accessibility
        }


# =============================================================================
# PERFORMANCE PLANNING
# =============================================================================

@dataclass
class PerformancePlan:
    """Performance plan"""
    image_optimization: Dict[str, Any] = field(default_factory=lambda: {
        "formats": ["webp", "avif"],
        "lazy_loading": True,
        "quality": 80
    })
    lazy_loading: bool = True
    code_splitting: Dict[str, Any] = field(default_factory=lambda: {
        "strategy": "route-based",
        "prefetch": True
    })
    font_loading: Dict[str, Any] = field(default_factory=lambda: {
        "strategy": "swap",
        "preload": True
    })
    animation_budget: Dict[str, Any] = field(default_factory=lambda: {
        "max_concurrent": 5,
        "max_duration_ms": 1000
    })
    third_party_dependencies: Dict[str, Any] = field(default_factory=dict)
    three_d_budget: Dict[str, Any] = field(default_factory=lambda: {"enabled": False})
    video_budget: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "max_size_mb": 5,
        "autoplay_muted": True
    })
    bundle_budget: Dict[str, Any] = field(default_factory=lambda: {
        "max_js_kb": 300,
        "max_css_kb": 50
    })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_optimization": self.image_optimization,
            "lazy_loading": self.lazy_loading,
            "code_splitting": self.code_splitting,
            "font_loading": self.font_loading,
            "animation_budget": self.animation_budget,
            "third_party_dependencies": self.third_party_dependencies,
            "three_d_budget": self.three_d_budget,
            "video_budget": self.video_budget,
            "bundle_budget": self.bundle_budget
        }


# =============================================================================
# IMPLEMENTATION PLANNING
# =============================================================================

@dataclass
class ImplementationStep:
    """Implementation step"""
    order: int
    task: str
    dependencies: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    validation: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "order": self.order,
            "task": self.task,
            "dependencies": self.dependencies,
            "files": self.files,
            "components": self.components,
            "validation": self.validation
        }


# =============================================================================
# MIGRATION PLANNING
# =============================================================================

@dataclass
class MigrationItem:
    """Migration item for existing code"""
    path: str
    action: CodeAction
    reason: str
    risk: str = "low"  # low, medium, high
    dependency: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "action": self.action.value,
            "reason": self.reason,
            "risk": self.risk,
            "dependency": self.dependency
        }


@dataclass
class MigrationPlan:
    """Migration plan for existing projects"""
    preserve: List[MigrationItem] = field(default_factory=list)
    modify: List[MigrationItem] = field(default_factory=list)
    replace: List[MigrationItem] = field(default_factory=list)
    remove: List[MigrationItem] = field(default_factory=list)
    create: List[MigrationItem] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "preserve": [item.to_dict() for item in self.preserve],
            "modify": [item.to_dict() for item in self.modify],
            "replace": [item.to_dict() for item in self.replace],
            "remove": [item.to_dict() for item in self.remove],
            "create": [item.to_dict() for item in self.create]
        }


# =============================================================================
# RESOURCE USAGE
# =============================================================================

@dataclass
class ResourceUsage:
    """Resource usage decision"""
    name: str
    enabled: bool
    reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "reason": self.reason
        }


# =============================================================================
# FILE PLAN
# =============================================================================

@dataclass
class FilePlan:
    """File structure plan"""
    path: str
    type: str  # file, directory
    purpose: str
    components: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "type": self.type,
            "purpose": self.purpose,
            "components": self.components,
            "dependencies": self.dependencies
        }


# =============================================================================
# DESIGN BUILD PLAN (MAIN OUTPUT)
# =============================================================================

@dataclass
class DesignBuildPlan:
    """Main output of the Design Execution Planner"""
    project: str
    framework: str = "react"
    styling_system: str = "tailwind"
    component_system: str = "custom"
    design_tokens: DesignTokens = field(default_factory=DesignTokens)
    pages: List[PagePlan] = field(default_factory=list)
    sections: List[SectionPlan] = field(default_factory=list)
    components: List[ComponentPlan] = field(default_factory=list)
    layout_plan: LayoutPlan = field(default_factory=LayoutPlan)
    typography_plan: TypographyTokens = field(default_factory=TypographyTokens)
    color_plan: ColorTokens = field(default_factory=ColorTokens)
    spacing_plan: SpacingTokens = field(default_factory=SpacingTokens)
    asset_plan: List[AssetPlan] = field(default_factory=list)
    motion_plan: List[MotionPlan] = field(default_factory=list)
    responsive_plan: ResponsivePlan = field(default_factory=ResponsivePlan)
    accessibility_plan: AccessibilityPlan = field(default_factory=AccessibilityPlan)
    performance_plan: PerformancePlan = field(default_factory=PerformancePlan)
    navigation: Dict[str, Any] = field(default_factory=dict)
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    implementation_order: List[ImplementationStep] = field(default_factory=list)
    validation_plan: List[str] = field(default_factory=list)
    resource_usage: List[ResourceUsage] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    migration_plan: Optional[MigrationPlan] = None
    file_plan: List[FilePlan] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "project": self.project,
            "framework": self.framework,
            "styling_system": self.styling_system,
            "component_system": self.component_system,
            "design_tokens": self.design_tokens.to_dict(),
            "pages": [p.to_dict() for p in self.pages],
            "sections": [s.to_dict() for s in self.sections],
            "components": [c.to_dict() for c in self.components],
            "layout_plan": self.layout_plan.to_dict(),
            "typography_plan": {k: v for k, v in self.typography_plan.__dict__.items()},
            "color_plan": {k: v for k, v in self.color_plan.__dict__.items()},
            "spacing_plan": {k: v for k, v in self.spacing_plan.__dict__.items()},
            "asset_plan": [a.to_dict() for a in self.asset_plan],
            "motion_plan": [m.to_dict() for m in self.motion_plan],
            "responsive_plan": self.responsive_plan.to_dict(),
            "accessibility_plan": self.accessibility_plan.to_dict(),
            "performance_plan": self.performance_plan.to_dict(),
            "navigation": self.navigation,
            "interactions": self.interactions,
            "dependencies": self.dependencies,
            "implementation_order": [i.to_dict() for i in self.implementation_order],
            "validation_plan": self.validation_plan,
            "resource_usage": [r.to_dict() for r in self.resource_usage],
            "risks": self.risks,
            "file_plan": [f.to_dict() for f in self.file_plan]
        }
        if self.migration_plan:
            result["migration_plan"] = self.migration_plan.to_dict()
        return result
    
    def validate(self) -> tuple[bool, List[str]]:
        """Validate the build plan"""
        errors = []
        
        # Required fields
        if not self.project:
            errors.append("Project name is required")
        
        # Pages validation
        if not self.pages:
            errors.append("At least one page plan is required")
        
        # Sections validation
        if not self.sections:
            errors.append("At least one section plan is required")
        
        # Components validation
        if not self.components:
            errors.append("At least one component plan is required")
        
        # Design tokens validation
        if not self.design_tokens:
            errors.append("Design tokens are required")
        
        # Implementation order validation
        if not self.implementation_order:
            errors.append("Implementation order is required")
        
        # Resource usage validation
        if not self.resource_usage:
            errors.append("Resource usage decisions are required")
        
        return len(errors) == 0, errors
