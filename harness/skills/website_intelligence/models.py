"""
Website Intelligence - Models for website design analysis
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class DesignStyle(Enum):
    """Design style categories"""
    MINIMALIST = "minimalist"
    MODERN = "modern"
    CLASSIC = "classic"
    BOLD = "bold"
    PLAYFUL = "playful"
    CORPORATE = "corporate"
    ARTISTIC = "artistic"
    VINTAGE = "vintage"
    FUTURISTIC = "futuristic"
    UNKNOWN = "unknown"


class ColorPaletteType(Enum):
    """Color palette types"""
    MONOCHROMATIC = "monochromatic"
    ANALOGOUS = "analogous"
    COMPLEMENTARY = "complementary"
    TRIADIC = "triadic"
    SPLIT_COMPLEMENTARY = "split_complementary"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


@dataclass
class ColorInfo:
    """Color information"""
    hex: str
    rgb: tuple[int, int, int] = field(default_factory=lambda: (0, 0, 0))
    usage: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hex": self.hex,
            "rgb": list(self.rgb),
            "usage": self.usage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorInfo':
        return cls(
            hex=data.get("hex", "#000000"),
            rgb=tuple(data.get("rgb", [0, 0, 0])),
            usage=data.get("usage", "unknown")
        )


@dataclass
class ColorPalette:
    """Color palette definition"""
    colors: List[ColorInfo] = field(default_factory=list)
    palette_type: ColorPaletteType = ColorPaletteType.UNKNOWN
    dominant_color: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "colors": [c.to_dict() for c in self.colors],
            "palette_type": self.palette_type.value,
            "dominant_color": self.dominant_color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ColorPalette':
        colors = [ColorInfo.from_dict(c) for c in data.get("colors", [])]
        return cls(
            colors=colors,
            palette_type=ColorPaletteType(data.get("palette_type", "unknown")),
            dominant_color=data.get("dominant_color")
        )


@dataclass
class Typography:
    """Typography settings"""
    font_families: List[str] = field(default_factory=list)
    font_sizes: Dict[str, str] = field(default_factory=dict)
    line_heights: Dict[str, float] = field(default_factory=dict)
    letter_spacing: Dict[str, str] = field(default_factory=dict)
    font_weights: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "font_families": self.font_families,
            "font_sizes": self.font_sizes,
            "line_heights": self.line_heights,
            "letter_spacing": self.letter_spacing,
            "font_weights": self.font_weights
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Typography':
        return cls(
            font_families=data.get("font_families", []),
            font_sizes=data.get("font_sizes", {}),
            line_heights=data.get("line_heights", {}),
            letter_spacing=data.get("letter_spacing", {}),
            font_weights=data.get("font_weights", {})
        )


@dataclass
class Layout:
    """Layout configuration"""
    grid_type: str = "unknown"
    columns: int = 0
    rows: int = 0
    container_width: str = "unknown"
    spacing: Dict[str, str] = field(default_factory=dict)
    alignment: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_type": self.grid_type,
            "columns": self.columns,
            "rows": self.rows,
            "container_width": self.container_width,
            "spacing": self.spacing,
            "alignment": self.alignment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Layout':
        return cls(
            grid_type=data.get("grid_type", "unknown"),
            columns=data.get("columns", 0),
            rows=data.get("rows", 0),
            container_width=data.get("container_width", "unknown"),
            spacing=data.get("spacing", {}),
            alignment=data.get("alignment", "unknown")
        )


@dataclass
class ComponentLibrary:
    """Component library information"""
    components: List[str] = field(default_factory=list)
    component_count: int = 0
    reusable_components: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components": self.components,
            "component_count": self.component_count,
            "reusable_components": self.reusable_components
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentLibrary':
        return cls(
            components=data.get("components", []),
            component_count=data.get("component_count", 0),
            reusable_components=data.get("reusable_components", [])
        )


@dataclass
class VisualDesign:
    """Visual design analysis"""
    style: DesignStyle = DesignStyle.UNKNOWN
    color_palette: Optional[ColorPalette] = None
    visual_hierarchy: str = "unknown"
    contrast_ratio: float = 0.0
    whitespace_usage: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style.value,
            "color_palette": self.color_palette.to_dict() if self.color_palette else None,
            "visual_hierarchy": self.visual_hierarchy,
            "contrast_ratio": self.contrast_ratio,
            "whitespace_usage": self.whitespace_usage
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualDesign':
        color_palette = None
        if data.get("color_palette"):
            color_palette = ColorPalette.from_dict(data["color_palette"])
        return cls(
            style=DesignStyle(data.get("style", "unknown")),
            color_palette=color_palette,
            visual_hierarchy=data.get("visual_hierarchy", "unknown"),
            contrast_ratio=data.get("contrast_ratio", 0.0),
            whitespace_usage=data.get("whitespace_usage", "unknown")
        )


@dataclass
class AccessibilityInfo:
    """Accessibility information"""
    wcag_level: str = "unknown"
    compliance_score: float = 0.0
    issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "wcag_level": self.wcag_level,
            "compliance_score": self.compliance_score,
            "issues": self.issues,
            "recommendations": self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccessibilityInfo':
        return cls(
            wcag_level=data.get("wcag_level", "unknown"),
            compliance_score=data.get("compliance_score", 0.0),
            issues=data.get("issues", []),
            recommendations=data.get("recommendations", [])
        )


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    load_time: float = 0.0
    first_contentful_paint: float = 0.0
    largest_contentful_paint: float = 0.0
    time_to_interactive: float = 0.0
    total_blocking_time: float = 0.0
    cumulative_layout_shift: float = 0.0
    lighthouse_score: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "load_time": self.load_time,
            "first_contentful_paint": self.first_contentful_paint,
            "largest_contentful_paint": self.largest_contentful_paint,
            "time_to_interactive": self.time_to_interactive,
            "total_blocking_time": self.total_blocking_time,
            "cumulative_layout_shift": self.cumulative_layout_shift,
            "lighthouse_score": self.lighthouse_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        return cls(
            load_time=data.get("load_time", 0.0),
            first_contentful_paint=data.get("first_contentful_paint", 0.0),
            largest_contentful_paint=data.get("largest_contentful_paint", 0.0),
            time_to_interactive=data.get("time_to_interactive", 0.0),
            total_blocking_time=data.get("total_blocking_time", 0.0),
            cumulative_layout_shift=data.get("cumulative_layout_shift", 0.0),
            lighthouse_score=data.get("lighthouse_score", 0)
        )


@dataclass
class AIQualityScore:
    """AI-generated content quality score"""
    overall_score: float = 0.0
    content_quality: float = 0.0
    design_coherence: float = 0.0
    user_experience: float = 0.0
    technical_quality: float = 0.0
    ai_confidence: float = 0.0
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "content_quality": self.content_quality,
            "design_coherence": self.design_coherence,
            "user_experience": self.user_experience,
            "technical_quality": self.technical_quality,
            "ai_confidence": self.ai_confidence,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIQualityScore':
        return cls(
            overall_score=data.get("overall_score", 0.0),
            content_quality=data.get("content_quality", 0.0),
            design_coherence=data.get("design_coherence", 0.0),
            user_experience=data.get("user_experience", 0.0),
            technical_quality=data.get("technical_quality", 0.0),
            ai_confidence=data.get("ai_confidence", 0.0),
            notes=data.get("notes", [])
        )


@dataclass
class TechnologyStack:
    """Technology stack information"""
    frontend_frameworks: List[str] = field(default_factory=list)
    backend_technologies: List[str] = field(default_factory=list)
    css_frameworks: List[str] = field(default_factory=list)
    build_tools: List[str] = field(default_factory=list)
    hosting_platform: str = "unknown"
    cms: Optional[str] = None
    analytics: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "frontend_frameworks": self.frontend_frameworks,
            "backend_technologies": self.backend_technologies,
            "css_frameworks": self.css_frameworks,
            "build_tools": self.build_tools,
            "hosting_platform": self.hosting_platform,
            "cms": self.cms,
            "analytics": self.analytics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TechnologyStack':
        return cls(
            frontend_frameworks=data.get("frontend_frameworks", []),
            backend_technologies=data.get("backend_technologies", []),
            css_frameworks=data.get("css_frameworks", []),
            build_tools=data.get("build_tools", []),
            hosting_platform=data.get("hosting_platform", "unknown"),
            cms=data.get("cms"),
            analytics=data.get("analytics", [])
        )


@dataclass
class WebsiteDesignProfile:
    """Complete website design profile"""
    project_name: str = "unknown"
    url: Optional[str] = None
    technology_stack: Optional[TechnologyStack] = None
    visual_design: Optional[VisualDesign] = None
    typography: Optional[Typography] = None
    layout: Optional[Layout] = None
    component_library: Optional[ComponentLibrary] = None
    accessibility: Optional[AccessibilityInfo] = None
    performance: Optional[PerformanceMetrics] = None
    ai_quality: Optional[AIQualityScore] = None
    patterns: List[str] = field(default_factory=list)
    motion_effects: List[str] = field(default_factory=list)
    assets: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "url": self.url,
            "technology_stack": self.technology_stack.to_dict() if self.technology_stack else None,
            "visual_design": self.visual_design.to_dict() if self.visual_design else None,
            "typography": self.typography.to_dict() if self.typography else None,
            "layout": self.layout.to_dict() if self.layout else None,
            "component_library": self.component_library.to_dict() if self.component_library else None,
            "accessibility": self.accessibility.to_dict() if self.accessibility else None,
            "performance": self.performance.to_dict() if self.performance else None,
            "ai_quality": self.ai_quality.to_dict() if self.ai_quality else None,
            "patterns": self.patterns,
            "motion_effects": self.motion_effects,
            "assets": self.assets
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebsiteDesignProfile':
        tech_stack = None
        if data.get("technology_stack"):
            tech_stack = TechnologyStack.from_dict(data["technology_stack"])
        
        visual_design = None
        if data.get("visual_design"):
            visual_design = VisualDesign.from_dict(data["visual_design"])
        
        typography = None
        if data.get("typography"):
            typography = Typography.from_dict(data["typography"])
        
        layout = None
        if data.get("layout"):
            layout = Layout.from_dict(data["layout"])
        
        component_lib = None
        if data.get("component_library"):
            component_lib = ComponentLibrary.from_dict(data["component_library"])
        
        accessibility = None
        if data.get("accessibility"):
            accessibility = AccessibilityInfo.from_dict(data["accessibility"])
        
        performance = None
        if data.get("performance"):
            performance = PerformanceMetrics.from_dict(data["performance"])
        
        ai_quality = None
        if data.get("ai_quality"):
            ai_quality = AIQualityScore.from_dict(data["ai_quality"])
        
        return cls(
            project_name=data.get("project_name", "unknown"),
            url=data.get("url"),
            technology_stack=tech_stack,
            visual_design=visual_design,
            typography=typography,
            layout=layout,
            component_library=component_lib,
            accessibility=accessibility,
            performance=performance,
            ai_quality=ai_quality,
            patterns=data.get("patterns", []),
            motion_effects=data.get("motion_effects", []),
            assets=data.get("assets", {})
        )
