"""
Registry - Load design resource hub skill into the skill registry
"""
from typing import Dict, Any, Optional
from harness.skills import load_skill, get_skill_registry

from .models import (
    DesignResourceResearchRequest,
    DesignResourceReport,
    ImageGenerationSkill,
    VideoGenerationSkill,
    AIQualityEvaluation,
)
from .catalog import DesignResourceCatalog
from .researcher import DesignResourceResearcher
from .selector import ResourceSelector


def design_resource_hub_execute(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for the Design Resource Hub skill.
    
    This function is called when the skill is executed via the skill registry.
    It performs resource research and selection based on project requirements.
    """
    if data is None:
        data = {}
    
    # Create request from input data
    request = DesignResourceResearchRequest(
        project_type=data.get("project_type", "landing_page"),
        industry=data.get("industry", "technology"),
        brand_personality=data.get("brand_personality", "modern"),
        visual_style=data.get("visual_style", "clean"),
        layout_style=data.get("layout_style", "standard"),
        animation_level=data.get("animation_level", "MEDIUM"),
        interaction_level=data.get("interaction_level", "MEDIUM"),
        _3d_required=data.get("_3d_required", False),
        asset_generation_required=data.get("asset_generation_required", False),
        performance_priority=data.get("performance_priority", "MEDIUM"),
        accessibility_priority=data.get("accessibility_priority", "HIGH"),
        originality_priority=data.get("originality_priority", "MEDIUM"),
        mobile_priority=data.get("mobile_priority", "HIGH"),
    )
    
    # Create selector and generate report
    catalog = DesignResourceCatalog()
    selector = ResourceSelector(catalog)
    
    task_id = data.get("task_id", "design-resource-task")
    context = data.get("context", {})
    
    report = selector.generate_report(request, task_id, context)
    
    return {
        "skill": "design-resource-hub",
        "status": "completed",
        "report": report.to_dict(),
        "minimum_stack": report.minimum_stack,
        "resources_selected": len(report.resources_selected),
        "resources_rejected": len(report.resources_rejected),
        "patterns_found": len(report.patterns_found),
        "confidence": report.confidence,
    }


def research_resources(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Research resources without full report generation"""
    if data is None:
        data = {}
    
    request = DesignResourceResearchRequest(
        project_type=data.get("project_type", "landing_page"),
        industry=data.get("industry", "technology"),
        brand_personality=data.get("brand_personality", "modern"),
        visual_style=data.get("visual_style", "clean"),
        layout_style=data.get("layout_style", "standard"),
        animation_level=data.get("animation_level", "MEDIUM"),
        interaction_level=data.get("interaction_level", "MEDIUM"),
        _3d_required=data.get("_3d_required", False),
        asset_generation_required=data.get("asset_generation_required", False),
        performance_priority=data.get("performance_priority", "MEDIUM"),
        accessibility_priority=data.get("accessibility_priority", "HIGH"),
        originality_priority=data.get("originality_priority", "MEDIUM"),
        mobile_priority=data.get("mobile_priority", "HIGH"),
    )
    
    catalog = DesignResourceCatalog()
    researcher = DesignResourceResearcher(catalog)
    
    result = researcher.research(request)
    
    return {
        "skill": "design-resource-hub-research",
        "status": "completed",
        "result": result,
    }


def get_catalog() -> Dict[str, Any]:
    """Get the full resource catalog"""
    catalog = DesignResourceCatalog()
    return {
        "skill": "design-resource-hub-catalog",
        "status": "completed",
        "catalog": catalog.to_dict(),
        "count": catalog.count_resources(),
    }


def create_image_generation_request(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create an image generation skill request"""
    if data is None:
        data = {}
    
    skill = ImageGenerationSkill(
        skill_name="Higgsfield",
        asset_type=data.get("asset_type", "image"),
        creative_direction=data.get("creative_direction", ""),
        style=data.get("style", ""),
        composition=data.get("composition", ""),
        aspect_ratio=data.get("aspect_ratio", "16:9"),
        purpose=data.get("purpose", ""),
    )
    
    return {
        "skill": "design-resource-hub-image-generation",
        "status": "completed",
        "request": skill.to_dict(),
    }


def create_video_generation_request(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a video generation skill request"""
    if data is None:
        data = {}
    
    skill = VideoGenerationSkill(
        skill_name="Higgsfield",
        asset_type="video",
        creative_direction=data.get("creative_direction", ""),
        style=data.get("style", ""),
        composition=data.get("composition", ""),
        aspect_ratio=data.get("aspect_ratio", "16:9"),
        duration=data.get("duration", 30.0),
        purpose=data.get("purpose", ""),
    )
    
    return {
        "skill": "design-resource-hub-video-generation",
        "status": "completed",
        "request": skill.to_dict(),
    }


def evaluate_ai_quality(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Evaluate design for AI-generated quality issues"""
    if data is None:
        data = {}
    
    evaluation = AIQualityEvaluation(
        originality=data.get("originality", 0.5),
        composition=data.get("composition", 0.5),
        typography=data.get("typography", 0.5),
        hierarchy=data.get("hierarchy", 0.5),
        brand_fit=data.get("brand_fit", 0.5),
        genericness=data.get("genericness", 0.5),
        repetition=data.get("repetition", 0.5),
        effect_overuse=data.get("effect_overuse", 0.5),
        visual_quality=data.get("visual_quality", 0.5),
        overall_score=data.get("overall_score", 0.5),
        issues=data.get("issues", []),
        recommendations=data.get("recommendations", []),
    )
    
    # Calculate overall score if not provided
    if "overall_score" not in data:
        scores = [
            evaluation.originality,
            evaluation.composition,
            evaluation.typography,
            evaluation.hierarchy,
            evaluation.brand_fit,
            1 - evaluation.genericness,  # Invert - lower genericness is better
            1 - evaluation.repetition,   # Invert
            1 - evaluation.effect_overuse,  # Invert
            evaluation.visual_quality,
        ]
        evaluation.overall_score = sum(scores) / len(scores)
    
    return {
        "skill": "design-resource-hub-ai-quality",
        "status": "completed",
        "evaluation": evaluation.to_dict(),
    }


def load_design_resource_hub_skill():
    """Load all design resource hub skills into the registry"""
    registry = get_skill_registry()
    
    # Register main skill
    registry.register_skill(
        name="design-resource-hub",
        description="Research and select design resources for a project",
        func=design_resource_hub_execute,
        category="design",
        version="0.1.0"
    )
    
    # Register research skill
    registry.register_skill(
        name="design-resource-research",
        description="Research design resources based on project requirements",
        func=research_resources,
        category="design",
        version="0.1.0"
    )
    
    # Register catalog skill
    registry.register_skill(
        name="design-resource-catalog",
        description="Get the full design resource catalog",
        func=get_catalog,
        category="design",
        version="0.1.0"
    )
    
    # Register image generation skill
    registry.register_skill(
        name="design-image-generation",
        description="Create image generation request for Higgsfield",
        func=create_image_generation_request,
        category="design",
        version="0.1.0"
    )
    
    # Register video generation skill
    registry.register_skill(
        name="design-video-generation",
        description="Create video generation request for Higgsfield",
        func=create_video_generation_request,
        category="design",
        version="0.1.0"
    )
    
    # Register AI quality evaluation skill
    registry.register_skill(
        name="design-ai-quality-evaluation",
        description="Evaluate design for AI-generated quality issues",
        func=evaluate_ai_quality,
        category="design",
        version="0.1.0"
    )
    
    # Also load via convenience function
    load_skill("design-resource-hub", design_resource_hub_execute)
    
    return True
