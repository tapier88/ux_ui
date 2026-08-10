"""
Redesign Intelligence Models - Structured representations for redesign strategy
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class ImprovementCategory(Enum):
    """Categories for improvements"""
    VISUAL = "visual"
    LAYOUT = "layout"
    TYPOGRAPHY = "typography"
    CONTENT = "content"
    CONVERSION = "conversion"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    INTERACTION = "interaction"
    RESPONSIVE = "responsive"


class LayoutPattern(Enum):
    """Available layout patterns"""
    ASYMMETRIC = "asymmetric"
    EDITORIAL = "editorial"
    BENTO = "bento"
    CENTERED = "centered"
    OVERLAPPING = "overlapping"
    IMMERSIVE = "immersive"
    SPLIT = "split"
    DIAGONAL = "diagonal"
    LAYERED = "layered"
    FULL_BLEED = "full-bleed"
    STORYTELLING = "storytelling"
    GRID = "grid"
    EXPERIMENTAL = "experimental"


class ComponentAction(Enum):
    """Actions for components"""
    PRESERVE = "preserve"
    REMOVE = "remove"
    MODIFY = "modify"
    REPLACE = "replace"
    CREATE = "create"


class Priority(Enum):
    """Priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PreserveDecision:
    """Decision to preserve an element"""
    element: str
    reason: str
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "reason": self.reason,
            "confidence": self.confidence
        }


@dataclass
class RemoveDecision:
    """Decision to remove an element"""
    element: str
    reason: str
    confidence: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "reason": self.reason,
            "confidence": self.confidence
        }


@dataclass
class ImproveDecision:
    """Decision to improve an element"""
    category: ImprovementCategory
    current_state: str
    problem: str
    proposed_change: str
    expected_benefit: str
    priority: Priority
    confidence: float = 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "current_state": self.current_state,
            "problem": self.problem,
            "proposed_change": self.proposed_change,
            "expected_benefit": self.expected_benefit,
            "priority": self.priority.value,
            "confidence": self.confidence
        }


@dataclass
class LayoutStrategy:
    """Layout strategy recommendations"""
    recommended_pattern: LayoutPattern
    alternative_patterns: List[LayoutPattern] = field(default_factory=list)
    reasoning: str = ""
    grid_system: Optional[str] = None
    spacing_scale: Optional[str] = None
    container_width: Optional[str] = None
    breakpoints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_pattern": self.recommended_pattern.value,
            "alternative_patterns": [p.value for p in self.alternative_patterns],
            "reasoning": self.reasoning,
            "grid_system": self.grid_system,
            "spacing_scale": self.spacing_scale,
            "container_width": self.container_width,
            "breakpoints": self.breakpoints
        }


@dataclass
class VisualStrategy:
    """Visual strategy recommendations"""
    density: str = ""  # low, medium, high
    negative_space: str = ""
    contrast_level: str = ""
    depth: str = ""
    hierarchy: str = ""
    rhythm: str = ""
    repetition: str = ""
    composition: str = ""
    scale_relationships: str = ""
    image_text_ratio: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "density": self.density,
            "negative_space": self.negative_space,
            "contrast_level": self.contrast_level,
            "depth": self.depth,
            "hierarchy": self.hierarchy,
            "rhythm": self.rhythm,
            "repetition": self.repetition,
            "composition": self.composition,
            "scale_relationships": self.scale_relationships,
            "image_text_ratio": self.image_text_ratio,
            "recommendations": self.recommendations
        }


@dataclass
class TypographyStrategy:
    """Typography strategy recommendations"""
    hierarchy: Dict[str, str] = field(default_factory=dict)  # H1, H2, H3, body, etc.
    font_sizes: Dict[str, str] = field(default_factory=dict)
    font_weights: Dict[str, str] = field(default_factory=dict)
    line_length: Optional[str] = None
    line_height: Optional[str] = None
    letter_spacing: Optional[str] = None
    font_combinations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hierarchy": self.hierarchy,
            "font_sizes": self.font_sizes,
            "font_weights": self.font_weights,
            "line_length": self.line_length,
            "line_height": self.line_height,
            "letter_spacing": self.letter_spacing,
            "font_combinations": self.font_combinations,
            "recommendations": self.recommendations
        }


@dataclass
class ColorStrategy:
    """Color strategy recommendations"""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    accent: Optional[str] = None
    background: Optional[str] = None
    foreground: Optional[str] = None
    muted: Optional[str] = None
    primary_ramp: Dict[str, str] = field(default_factory=dict)
    semantic_colors: Dict[str, str] = field(default_factory=dict)
    brand_preservation: bool = True
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "foreground": self.foreground,
            "muted": self.muted,
            "primary_ramp": self.primary_ramp,
            "semantic_colors": self.semantic_colors,
            "brand_preservation": self.brand_preservation,
            "recommendations": self.recommendations
        }


@dataclass
class ComponentRecommendation:
    """Recommendation for a component"""
    component_name: str
    action: ComponentAction
    reason: str
    source: Optional[str] = None  # shadcn, Radix, React Bits, MagicUI, Lucide, etc.
    alternatives: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "action": self.action.value,
            "reason": self.reason,
            "source": self.source,
            "alternatives": self.alternatives
        }


@dataclass
class ComponentStrategy:
    """Component strategy recommendations"""
    components: List[ComponentRecommendation] = field(default_factory=list)
    minimum_stack_principle: bool = True
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": [c.to_dict() for c in self.components],
            "minimum_stack_principle": self.minimum_stack_principle,
            "recommendations": self.recommendations
        }


@dataclass
class MotionStrategy:
    """Motion strategy recommendations"""
    use_animation: bool = True
    intensity: str = ""  # none, subtle, moderate, expressive
    duration_range: Optional[str] = None
    animated_elements: List[str] = field(default_factory=list)
    static_elements: List[str] = field(default_factory=list)
    performance_priority: bool = True
    accessibility_considerations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "use_animation": self.use_animation,
            "intensity": self.intensity,
            "duration_range": self.duration_range,
            "animated_elements": self.animated_elements,
            "static_elements": self.static_elements,
            "performance_priority": self.performance_priority,
            "accessibility_considerations": self.accessibility_considerations,
            "recommendations": self.recommendations
        }


@dataclass
class ContentHierarchyStrategy:
    """Content hierarchy strategy"""
    primary_content: List[str] = field(default_factory=list)
    secondary_content: List[str] = field(default_factory=list)
    tertiary_content: List[str] = field(default_factory=list)
    content_flow: List[str] = field(default_factory=list)
    fold_strategy: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_content": self.primary_content,
            "secondary_content": self.secondary_content,
            "tertiary_content": self.tertiary_content,
            "content_flow": self.content_flow,
            "fold_strategy": self.fold_strategy,
            "recommendations": self.recommendations
        }


@dataclass
class PerformanceStrategy:
    """Performance strategy recommendations"""
    image_optimization: List[str] = field(default_factory=list)
    js_optimization: List[str] = field(default_factory=list)
    animation_optimization: List[str] = field(default_factory=list)
    dependency_optimization: List[str] = field(default_factory=list)
    font_optimization: List[str] = field(default_factory=list)
    lazy_loading: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_optimization": self.image_optimization,
            "js_optimization": self.js_optimization,
            "animation_optimization": self.animation_optimization,
            "dependency_optimization": self.dependency_optimization,
            "font_optimization": self.font_optimization,
            "lazy_loading": self.lazy_loading,
            "recommendations": self.recommendations
        }


@dataclass
class AccessibilityStrategy:
    """Accessibility strategy recommendations"""
    contrast_issues: List[Dict[str, Any]] = field(default_factory=list)
    focus_management: List[str] = field(default_factory=list)
    keyboard_navigation: List[str] = field(default_factory=list)
    semantic_html: List[str] = field(default_factory=list)
    aria_requirements: List[str] = field(default_factory=list)
    motion_sensitivity: List[str] = field(default_factory=list)
    touch_targets: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contrast_issues": self.contrast_issues,
            "focus_management": self.focus_management,
            "keyboard_navigation": self.keyboard_navigation,
            "semantic_html": self.semantic_html,
            "aria_requirements": self.aria_requirements,
            "motion_sensitivity": self.motion_sensitivity,
            "touch_targets": self.touch_targets,
            "recommendations": self.recommendations
        }


@dataclass
class DesignRisk:
    """Identified design risk"""
    risk: str
    severity: str  # low, medium, high, critical
    likelihood: str  # low, medium, high
    impact: str
    mitigation: str
    confidence: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk": self.risk,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "mitigation": self.mitigation,
            "confidence": self.confidence
        }


@dataclass
class RedesignStrategy:
    """Complete redesign strategy"""
    project_summary: str = ""
    original_analysis: str = ""
    preserve: List[PreserveDecision] = field(default_factory=list)
    remove: List[RemoveDecision] = field(default_factory=list)
    improve: List[ImproveDecision] = field(default_factory=list)
    restructure: List[str] = field(default_factory=list)
    visual_strategy: Optional[VisualStrategy] = None
    layout_strategy: Optional[LayoutStrategy] = None
    typography_strategy: Optional[TypographyStrategy] = None
    color_strategy: Optional[ColorStrategy] = None
    component_strategy: Optional[ComponentStrategy] = None
    motion_strategy: Optional[MotionStrategy] = None
    content_hierarchy: Optional[ContentHierarchyStrategy] = None
    performance_strategy: Optional[PerformanceStrategy] = None
    accessibility_strategy: Optional[AccessibilityStrategy] = None
    risks: List[DesignRisk] = field(default_factory=list)
    recommended_patterns: List[str] = field(default_factory=list)
    recommended_resources: List[str] = field(default_factory=list)
    confidence: float = 0.75
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_summary": self.project_summary,
            "original_analysis": self.original_analysis,
            "preserve": [p.to_dict() for p in self.preserve],
            "remove": [r.to_dict() for r in self.remove],
            "improve": [i.to_dict() for i in self.improve],
            "restructure": self.restructure,
            "visual_strategy": self.visual_strategy.to_dict() if self.visual_strategy else None,
            "layout_strategy": self.layout_strategy.to_dict() if self.layout_strategy else None,
            "typography_strategy": self.typography_strategy.to_dict() if self.typography_strategy else None,
            "color_strategy": self.color_strategy.to_dict() if self.color_strategy else None,
            "component_strategy": self.component_strategy.to_dict() if self.component_strategy else None,
            "motion_strategy": self.motion_strategy.to_dict() if self.motion_strategy else None,
            "content_hierarchy": self.content_hierarchy.to_dict() if self.content_hierarchy else None,
            "performance_strategy": self.performance_strategy.to_dict() if self.performance_strategy else None,
            "accessibility_strategy": self.accessibility_strategy.to_dict() if self.accessibility_strategy else None,
            "risks": [r.to_dict() for r in self.risks],
            "recommended_patterns": self.recommended_patterns,
            "recommended_resources": self.recommended_resources,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }
