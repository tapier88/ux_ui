"""
Data models for Website Intelligence
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json


@dataclass
class TechnologyStack:
    """Technology stack detected in a website"""
    framework: str = "unknown"
    language: str = "unknown"
    build_tools: List[str] = field(default_factory=list)
    libraries: List[str] = field(default_factory=list)
    css_framework: str = "unknown"
    bundler: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework": self.framework,
            "language": self.language,
            "build_tools": self.build_tools,
            "libraries": self.libraries,
            "css_framework": self.css_framework,
            "bundler": self.bundler
        }


@dataclass
class VisualDesign:
    """Visual design characteristics"""
    color_palette: List[str] = field(default_factory=list)
    primary_color: str = "unknown"
    secondary_color: str = "unknown"
    accent_color: str = "unknown"
    background_color: str = "unknown"
    text_color: str = "unknown"
    has_dark_mode: bool = False
    style: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "color_palette": self.color_palette,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "accent_color": self.accent_color,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "has_dark_mode": self.has_dark_mode,
            "style": self.style
        }


@dataclass
class Typography:
    """Typography information"""
    font_family: str = "unknown"
    font_sizes: Dict[str, str] = field(default_factory=dict)
    line_heights: Dict[str, str] = field(default_factory=dict)
    font_weights: Dict[str, str] = field(default_factory=dict)
    google_fonts: List[str] = field(default_factory=list)
    custom_fonts: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "font_family": self.font_family,
            "font_sizes": self.font_sizes,
            "line_heights": self.line_heights,
            "font_weights": self.font_weights,
            "google_fonts": self.google_fonts,
            "custom_fonts": self.custom_fonts
        }


@dataclass
class Layout:
    """Layout structure information"""
    type: str = "unknown"
    grid_system: str = "unknown"
    container_width: str = "unknown"
    breakpoints: List[str] = field(default_factory=list)
    sections: List[str] = field(default_factory=list)
    navigation_type: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "grid_system": self.grid_system,
            "container_width": self.container_width,
            "breakpoints": self.breakpoints,
            "sections": self.sections,
            "navigation_type": self.navigation_type
        }


@dataclass
class ComponentLibrary:
    """Component library information"""
    components: List[str] = field(default_factory=list)
    ui_library: str = "unknown"
    icon_library: str = "unknown"
    custom_components: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": self.components,
            "ui_library": self.ui_library,
            "icon_library": self.icon_library,
            "custom_components": self.custom_components
        }


@dataclass
class AccessibilityInfo:
    """Accessibility information"""
    score: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    aria_labels: int = 0
    alt_texts_missing: int = 0
    contrast_issues: int = 0
    keyboard_navigation: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "issues": self.issues,
            "aria_labels": self.aria_labels,
            "alt_texts_missing": self.alt_texts_missing,
            "contrast_issues": self.contrast_issues,
            "keyboard_navigation": self.keyboard_navigation
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    load_time_ms: int = 0
    first_contentful_paint_ms: int = 0
    largest_contentful_paint_ms: int = 0
    time_to_interactive_ms: int = 0
    total_blocking_time_ms: int = 0
    cumulative_layout_shift: float = 0.0
    bundle_size_kb: int = 0
    image_optimization: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "load_time_ms": self.load_time_ms,
            "first_contentful_paint_ms": self.first_contentful_paint_ms,
            "largest_contentful_paint_ms": self.largest_contentful_paint_ms,
            "time_to_interactive_ms": self.time_to_interactive_ms,
            "total_blocking_time_ms": self.total_blocking_time_ms,
            "cumulative_layout_shift": self.cumulative_layout_shift,
            "bundle_size_kb": self.bundle_size_kb,
            "image_optimization": self.image_optimization
        }


@dataclass
class AIQualityScore:
    """AI-generated content quality assessment"""
    overall_score: float = 0.0
    content_quality: str = "unknown"
    code_quality: str = "unknown"
    design_consistency: str = "unknown"
    originality: str = "unknown"
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "content_quality": self.content_quality,
            "code_quality": self.code_quality,
            "design_consistency": self.design_consistency,
            "originality": self.originality,
            "recommendations": self.recommendations
        }


@dataclass
class WebsiteDesignProfile:
    """Complete design profile for a website"""
    project_name: str = ""
    url: str = ""
    technology: TechnologyStack = field(default_factory=TechnologyStack)
    visual: VisualDesign = field(default_factory=VisualDesign)
    typography: Typography = field(default_factory=Typography)
    layout: Layout = field(default_factory=Layout)
    components: ComponentLibrary = field(default_factory=ComponentLibrary)
    accessibility: AccessibilityInfo = field(default_factory=AccessibilityInfo)
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    ai_quality: AIQualityScore = field(default_factory=AIQualityScore)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "url": self.url,
            "technology": self.technology.to_dict(),
            "visual": self.visual.to_dict(),
            "typography": self.typography.to_dict(),
            "layout": self.layout.to_dict(),
            "components": self.components.to_dict(),
            "accessibility": self.accessibility.to_dict(),
            "performance": self.performance.to_dict(),
            "ai_quality": self.ai_quality.to_dict()
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
