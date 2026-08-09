"""
Design Execution Planner - Converts design decisions into technical build plans
"""
from .models import (
    DesignBuildPlan, PagePlan, SectionPlan, ComponentPlan, LayoutPlan,
    AssetPlan, MotionPlan, ResponsivePlan, AccessibilityPlan, PerformancePlan,
    ImplementationStep, FilePlan, MigrationPlan, ResourceUsage,
    DesignTokens, ColorTokens, TypographyTokens, SpacingTokens,
    LayoutType, AnimationType, AssetType, ResourceSource, CodeAction,
    GenerationRequest
)
from .planner import DesignExecutionPlanner
from .component_planner import ComponentPlanner
from .layout_planner import LayoutPlanner
from .motion_planner import MotionPlanner
from .asset_planner import AssetPlanner
from .responsive_planner import ResponsivePlanner
from .accessibility_planner import AccessibilityPlanner
from .performance_planner import PerformancePlanner
from .validation import PlanValidator

__all__ = [
    # Main orchestrator
    "DesignExecutionPlanner",
    
    # Specialist planners
    "ComponentPlanner",
    "LayoutPlanner",
    "MotionPlanner",
    "AssetPlanner",
    "ResponsivePlanner",
    "AccessibilityPlanner",
    "PerformancePlanner",
    "PlanValidator",
    
    # Models
    "DesignBuildPlan",
    "PagePlan",
    "SectionPlan",
    "ComponentPlan",
    "LayoutPlan",
    "AssetPlan",
    "MotionPlan",
    "ResponsivePlan",
    "AccessibilityPlan",
    "PerformancePlan",
    "ImplementationStep",
    "FilePlan",
    "MigrationPlan",
    "ResourceUsage",
    "DesignTokens",
    "ColorTokens",
    "TypographyTokens",
    "SpacingTokens",
    "GenerationRequest",
    
    # Enums
    "LayoutType",
    "AnimationType",
    "AssetType",
    "ResourceSource",
    "CodeAction"
]


def create_planner() -> DesignExecutionPlanner:
    """Create a new DesignExecutionPlanner instance"""
    return DesignExecutionPlanner()


def load_into_registry(registry):
    """Load the skill into a registry"""
    from harness.skills import load_skill
    
    def execute_design_planning(
        project_name: str,
        design_profile: dict = None,
        redesign_strategy: dict = None,
        resource_report: dict = None,
        existing_code: dict = None
    ) -> dict:
        """Execute design planning and return build plan as dict"""
        planner = DesignExecutionPlanner()
        plan = planner.create_build_plan(
            project_name=project_name,
            design_profile=design_profile,
            redesign_strategy=redesign_strategy,
            resource_report=resource_report,
            existing_code=existing_code
        )
        return plan.to_dict()
    
    load_skill("design-execution-planner", execute_design_planning)
