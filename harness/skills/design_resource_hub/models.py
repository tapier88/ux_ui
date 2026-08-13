"""
Models for Design Resource Hub
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from harness.core.time import utc_now_iso


class ResourceType(Enum):
    """Types of design resources"""
    LIBRARY = "library"
    FRAMEWORK = "framework"
    COMPONENT_LIBRARY = "component_library"
    ANIMATION_LIBRARY = "animation_library"
    DESIGN_SYSTEM = "design_system"
    ASSET_LIBRARY = "asset_library"
    GENERATION_SKILL = "generation_skill"
    QUALITY_SKILL = "quality_skill"
    RESEARCH_RESOURCE = "research_resource"
    TOOL = "tool"


class ResourceCategory(Enum):
    """Categories for design resources"""
    FOUNDATION = "foundation"
    STYLING = "styling"
    COMPONENTS = "components"
    ANIMATION = "animation"
    THREE_D = "3d"
    ICONOGRAPHY = "iconography"
    TYPOGRAPHY = "typography"
    DESIGN_SYSTEM = "design_system"
    DEVELOPMENT = "development"
    DESIGN_RESOURCES = "design_resources"
    AI_TOOLS = "ai_tools"
    QUALITY = "quality"


class ResourceStatus(Enum):
    """Status of a resource"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    PENDING_RESOURCE = "pending_resource"
    UNKNOWN = "unknown"


@dataclass
class DesignResource:
    """Represents a design resource in the catalog"""
    id: str
    name: str
    type: ResourceType
    category: ResourceCategory
    repository: Optional[str] = None
    official_url: Optional[str] = None
    purpose: str = ""
    capabilities: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    recommended_for: List[str] = field(default_factory=list)
    avoid_when: List[str] = field(default_factory=list)
    technology: List[str] = field(default_factory=list)
    license: str = "unknown"
    commercial_use: bool = True
    research_priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH, VERY HIGH
    implementation_priority: str = "MEDIUM"
    status: ResourceStatus = ResourceStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "category": self.category.value,
            "repository": self.repository,
            "official_url": self.official_url,
            "purpose": self.purpose,
            "capabilities": self.capabilities,
            "strengths": self.strengths,
            "limitations": self.limitations,
            "recommended_for": self.recommended_for,
            "avoid_when": self.avoid_when,
            "technology": self.technology,
            "license": self.license,
            "commercial_use": self.commercial_use,
            "research_priority": self.research_priority,
            "implementation_priority": self.implementation_priority,
            "status": self.status.value,
            "metadata": self.metadata,
        }


@dataclass
class DesignResourceResearchRequest:
    """Request for researching design resources"""
    project_type: str
    industry: str
    brand_personality: str
    visual_style: str
    layout_style: str
    animation_level: str  # NONE, LOW, MEDIUM, HIGH
    interaction_level: str  # NONE, LOW, MEDIUM, HIGH
    _3d_required: bool = False
    asset_generation_required: bool = False
    performance_priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    accessibility_priority: str = "HIGH"  # LOW, MEDIUM, HIGH
    originality_priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    mobile_priority: str = "HIGH"  # LOW, MEDIUM, HIGH
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_type": self.project_type,
            "industry": self.industry,
            "brand_personality": self.brand_personality,
            "visual_style": self.visual_style,
            "layout_style": self.layout_style,
            "animation_level": self.animation_level,
            "interaction_level": self.interaction_level,
            "_3d_required": self._3d_required,
            "asset_generation_required": self.asset_generation_required,
            "performance_priority": self.performance_priority,
            "accessibility_priority": self.accessibility_priority,
            "originality_priority": self.originality_priority,
            "mobile_priority": self.mobile_priority,
            "metadata": self.metadata,
        }


@dataclass
class ResourceDecision:
    """Decision about whether to use a resource"""
    resource: DesignResource
    selected: bool
    score: float = 0.0
    reason: str = ""
    alternative: Optional[str] = None
    complexity: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    performance_cost: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    accessibility_impact: str = "POSITIVE"  # NEGATIVE, NEUTRAL, POSITIVE
    visual_fit: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    project_fit: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource.id,
            "resource_name": self.resource.name,
            "selected": self.selected,
            "score": self.score,
            "reason": self.reason,
            "alternative": self.alternative,
            "complexity": self.complexity,
            "performance_cost": self.performance_cost,
            "accessibility_impact": self.accessibility_impact,
            "visual_fit": self.visual_fit,
            "project_fit": self.project_fit,
            "confidence": self.confidence,
        }


@dataclass
class DesignInspiration:
    """Inspiration extracted from a resource"""
    source: str  # Resource ID or name
    resource: str  # Resource name
    pattern: str  # Pattern name (e.g., hero_split, bento, fade_up)
    description: str
    why_relevant: str
    adaptation: str  # How to adapt for current project
    complexity: str = "MEDIUM"
    performance: str = "MEDIUM"
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "resource": self.resource,
            "pattern": self.pattern,
            "description": self.description,
            "why_relevant": self.why_relevant,
            "adaptation": self.adaptation,
            "complexity": self.complexity,
            "performance": self.performance,
            "confidence": self.confidence,
        }


@dataclass
class ImageGenerationSkill:
    """Abstraction for image generation capability (e.g., Higgsfield)"""
    skill_name: str = "Higgsfield"
    asset_type: str = "image"  # image, video
    creative_direction: str = ""
    style: str = ""
    composition: str = ""
    aspect_ratio: str = "16:9"
    duration: Optional[float] = None  # For video
    purpose: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "asset_type": self.asset_type,
            "creative_direction": self.creative_direction,
            "style": self.style,
            "composition": self.composition,
            "aspect_ratio": self.aspect_ratio,
            "duration": self.duration,
            "purpose": self.purpose,
            "metadata": self.metadata,
        }


@dataclass
class VideoGenerationSkill:
    """Abstraction for video generation capability"""
    skill_name: str = "Higgsfield"
    asset_type: str = "video"
    creative_direction: str = ""
    style: str = ""
    composition: str = ""
    aspect_ratio: str = "16:9"
    duration: float = 30.0
    purpose: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "asset_type": self.asset_type,
            "creative_direction": self.creative_direction,
            "style": self.style,
            "composition": self.composition,
            "aspect_ratio": self.aspect_ratio,
            "duration": self.duration,
            "purpose": self.purpose,
            "metadata": self.metadata,
        }


@dataclass
class AIQualityEvaluation:
    """Evaluation of design quality to detect AI-generated slop"""
    originality: float = 0.5  # 0-1 scale
    composition: float = 0.5
    typography: float = 0.5
    hierarchy: float = 0.5
    brand_fit: float = 0.5
    genericness: float = 0.5  # Higher = more generic
    repetition: float = 0.5  # Higher = more repetitive
    effect_overuse: float = 0.5  # Higher = more overused effects
    visual_quality: float = 0.5
    overall_score: float = 0.5
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "originality": self.originality,
            "composition": self.composition,
            "typography": self.typography,
            "hierarchy": self.hierarchy,
            "brand_fit": self.brand_fit,
            "genericness": self.genericness,
            "repetition": self.repetition,
            "effect_overuse": self.effect_overuse,
            "visual_quality": self.visual_quality,
            "overall_score": self.overall_score,
            "issues": self.issues,
            "recommendations": self.recommendations,
        }


@dataclass
class DesignResourceReport:
    """Report generated after resource research"""
    task_id: str
    timestamp: str = field(default_factory=utc_now_iso)
    project_analysis: Dict[str, Any] = field(default_factory=dict)
    resources_consulted: List[str] = field(default_factory=list)
    resources_selected: List[ResourceDecision] = field(default_factory=list)
    resources_rejected: List[ResourceDecision] = field(default_factory=list)
    patterns_found: List[DesignInspiration] = field(default_factory=list)
    animation_ideas: List[DesignInspiration] = field(default_factory=list)
    layout_ideas: List[DesignInspiration] = field(default_factory=list)
    component_ideas: List[DesignInspiration] = field(default_factory=list)
    typography_ideas: List[DesignInspiration] = field(default_factory=list)
    visual_ideas: List[DesignInspiration] = field(default_factory=list)
    asset_ideas: List[DesignInspiration] = field(default_factory=list)
    implementation_recommendations: List[str] = field(default_factory=list)
    performance_notes: List[str] = field(default_factory=list)
    accessibility_notes: List[str] = field(default_factory=list)
    license_notes: List[str] = field(default_factory=list)
    design_diversity_notes: List[str] = field(default_factory=list)
    confidence: float = 0.5
    minimum_stack: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "project_analysis": self.project_analysis,
            "resources_consulted": self.resources_consulted,
            "resources_selected": [d.to_dict() for d in self.resources_selected],
            "resources_rejected": [d.to_dict() for d in self.resources_rejected],
            "patterns_found": [p.to_dict() for p in self.patterns_found],
            "animation_ideas": [i.to_dict() for i in self.animation_ideas],
            "layout_ideas": [i.to_dict() for i in self.layout_ideas],
            "component_ideas": [i.to_dict() for i in self.component_ideas],
            "typography_ideas": [i.to_dict() for i in self.typography_ideas],
            "visual_ideas": [i.to_dict() for i in self.visual_ideas],
            "asset_ideas": [i.to_dict() for i in self.asset_ideas],
            "implementation_recommendations": self.implementation_recommendations,
            "performance_notes": self.performance_notes,
            "accessibility_notes": self.accessibility_notes,
            "license_notes": self.license_notes,
            "design_diversity_notes": self.design_diversity_notes,
            "confidence": self.confidence,
            "minimum_stack": self.minimum_stack,
        }
