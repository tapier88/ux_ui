"""
Models for Redesign Intelligence

These models represent the structured output of the redesign analysis,
including decisions about what to preserve, remove, improve, and strategies
for layout, visual design, typography, color, components, motion, accessibility,
and performance.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PreserveDecision:
    """Decision about an element to preserve from the original design"""
    element: str
    reason: str
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "reason": self.reason,
            "confidence": self.confidence,
        }


@dataclass
class RemoveDecision:
    """Decision about an element to remove from the original design"""
    element: str
    reason: str
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "reason": self.reason,
            "confidence": self.confidence,
        }


@dataclass
class ImproveDecision:
    """Decision about an element to improve in the original design"""
    category: str  # visual, layout, typography, content, conversion, accessibility, performance, interaction, responsive
    current_state: str
    problem: str
    proposed_change: str
    expected_benefit: str
    priority: str = "medium"  # low, medium, high, critical
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "current_state": self.current_state,
            "problem": self.problem,
            "proposed_change": self.proposed_change,
            "expected_benefit": self.expected_benefit,
            "priority": self.priority,
            "confidence": self.confidence,
        }


@dataclass
class LayoutStrategy:
    """Strategy for layout recommendations"""
    pattern: str  # asymmetric, editorial, bento, centered, overlapping, immersive, split, diagonal, layered, full-bleed, storytelling, grid, experimental
    description: str
    reasoning: str
    sections: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern,
            "description": self.description,
            "reasoning": self.reasoning,
            "sections": self.sections,
        }


@dataclass
class VisualStrategy:
    """Strategy for visual design recommendations"""
    density: str  # low, medium, high
    negative_space: str
    contrast_level: str  # low, medium, high
    depth: str
    hierarchy: str
    rhythm: str
    composition_notes: str
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "density": self.density,
            "negative_space": self.negative_space,
            "contrast_level": self.contrast_level,
            "depth": self.depth,
            "hierarchy": self.hierarchy,
            "rhythm": self.rhythm,
            "composition_notes": self.composition_notes,
            "recommendations": self.recommendations,
        }


@dataclass
class TypographyStrategy:
    """Strategy for typography recommendations"""
    hierarchy: Dict[str, str] = field(default_factory=dict)  # H1, H2, H3, body, etc.
    primary_font: Optional[str] = None
    secondary_font: Optional[str] = None
    sizes: Dict[str, str] = field(default_factory=dict)
    weights: Dict[str, str] = field(default_factory=dict)
    line_length: str = ""
    line_height: str = ""
    letter_spacing: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hierarchy": self.hierarchy,
            "primary_font": self.primary_font,
            "secondary_font": self.secondary_font,
            "sizes": self.sizes,
            "weights": self.weights,
            "line_length": self.line_length,
            "line_height": self.line_height,
            "letter_spacing": self.letter_spacing,
            "recommendations": self.recommendations,
        }


@dataclass
class ColorStrategy:
    """Strategy for color recommendations"""
    primary: Optional[str] = None
    secondary: Optional[str] = None
    accent: Optional[str] = None
    background: Optional[str] = None
    foreground: Optional[str] = None
    muted: Optional[str] = None
    semantic: Dict[str, str] = field(default_factory=dict)  # success, warning, error, info
    brand_preservation_notes: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "foreground": self.foreground,
            "muted": self.muted,
            "semantic": self.semantic,
            "brand_preservation_notes": self.brand_preservation_notes,
            "recommendations": self.recommendations,
        }


@dataclass
class ComponentStrategy:
    """Strategy for component recommendations"""
    preserve: List[str] = field(default_factory=list)
    remove: List[str] = field(default_factory=list)
    modify: List[Dict[str, str]] = field(default_factory=list)
    replace: List[Dict[str, str]] = field(default_factory=list)
    create: List[str] = field(default_factory=list)
    recommended_libraries: List[str] = field(default_factory=list)  # shadcn, Radix, React Bits, MagicUI, Lucide
    minimum_stack_principle: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "preserve": self.preserve,
            "remove": self.remove,
            "modify": self.modify,
            "replace": self.replace,
            "create": self.create,
            "recommended_libraries": self.recommended_libraries,
            "minimum_stack_principle": self.minimum_stack_principle,
        }


@dataclass
class MotionStrategy:
    """Strategy for motion/animation recommendations"""
    use_animation: bool = True
    intensity: str = "medium"  # none, low, medium, high
    duration_range: str = ""
    where_to_use: List[str] = field(default_factory=list)
    where_to_avoid: List[str] = field(default_factory=list)
    accessibility_considerations: List[str] = field(default_factory=list)
    performance_impact: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "use_animation": self.use_animation,
            "intensity": self.intensity,
            "duration_range": self.duration_range,
            "where_to_use": self.where_to_use,
            "where_to_avoid": self.where_to_avoid,
            "accessibility_considerations": self.accessibility_considerations,
            "performance_impact": self.performance_impact,
            "recommendations": self.recommendations,
        }


@dataclass
class ContentHierarchyStrategy:
    """Strategy for content hierarchy"""
    primary_content: List[str] = field(default_factory=list)
    secondary_content: List[str] = field(default_factory=list)
    tertiary_content: List[str] = field(default_factory=list)
    fold_priority: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_content": self.primary_content,
            "secondary_content": self.secondary_content,
            "tertiary_content": self.tertiary_content,
            "fold_priority": self.fold_priority,
            "recommendations": self.recommendations,
        }


@dataclass
class PerformanceStrategy:
    """Strategy for performance optimization"""
    image_optimization: List[str] = field(default_factory=list)
    js_optimization: List[str] = field(default_factory=list)
    font_optimization: List[str] = field(default_factory=list)
    animation_optimization: List[str] = field(default_factory=list)
    dependency_optimization: List[str] = field(default_factory=list)
    lazy_loading: List[str] = field(default_factory=list)
    caching_strategy: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_optimization": self.image_optimization,
            "js_optimization": self.js_optimization,
            "font_optimization": self.font_optimization,
            "animation_optimization": self.animation_optimization,
            "dependency_optimization": self.dependency_optimization,
            "lazy_loading": self.lazy_loading,
            "caching_strategy": self.caching_strategy,
            "recommendations": self.recommendations,
        }


@dataclass
class AccessibilityStrategy:
    """Strategy for accessibility improvements"""
    contrast_issues: List[Dict[str, Any]] = field(default_factory=list)
    focus_management: List[str] = field(default_factory=list)
    keyboard_navigation: List[str] = field(default_factory=list)
    semantic_html: List[str] = field(default_factory=list)
    aria_recommendations: List[str] = field(default_factory=list)
    motion_sensitivity: List[str] = field(default_factory=list)
    touch_targets: List[str] = field(default_factory=list)
    wcag_level: str = "AA"
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contrast_issues": self.contrast_issues,
            "focus_management": self.focus_management,
            "keyboard_navigation": self.keyboard_navigation,
            "semantic_html": self.semantic_html,
            "aria_recommendations": self.aria_recommendations,
            "motion_sensitivity": self.motion_sensitivity,
            "touch_targets": self.touch_targets,
            "wcag_level": self.wcag_level,
            "recommendations": self.recommendations,
        }


@dataclass
class DesignRisk:
    """Identified design risk"""
    risk: str
    severity: str  # low, medium, high, critical
    likelihood: str  # low, medium, high
    impact: str
    mitigation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk": self.risk,
            "severity": self.severity,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "mitigation": self.mitigation,
        }


@dataclass
class RedesignStrategy:
    """Main output of the Redesign Intelligence Engine"""
    project_summary: str = ""
    original_analysis: str = ""
    preserve: List[PreserveDecision] = field(default_factory=list)
    remove: List[RemoveDecision] = field(default_factory=list)
    improve: List[ImproveDecision] = field(default_factory=list)
    restructure: List[Dict[str, Any]] = field(default_factory=list)
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
    confidence: float = 0.0
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
            "reasoning": self.reasoning,
        }
