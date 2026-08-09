"""
Redesign Intelligence Skill V0.1

Transforms WebsiteDesignProfile into RedesignStrategy

This skill analyzes a website design profile and produces comprehensive
redesign recommendations including:
- What to preserve
- What to remove
- What to improve
- Layout strategy
- Visual strategy
- Typography strategy
- Color strategy
- Component strategy
- Motion strategy
- Content hierarchy
- Performance strategy
- Accessibility strategy
- Risk assessment
"""

from .models import (
    RedesignStrategy,
    PreserveDecision,
    RemoveDecision,
    ImproveDecision,
    LayoutStrategy,
    VisualStrategy,
    TypographyStrategy,
    ColorStrategy,
    ComponentStrategy,
    ComponentRecommendation,
    MotionStrategy,
    ContentHierarchyStrategy,
    PerformanceStrategy,
    AccessibilityStrategy,
    DesignRisk,
    ImprovementCategory,
    LayoutPattern,
    ComponentAction,
    Priority,
)

from .engine import (
    RedesignIntelligenceEngine,
    PreserveEngine,
    RemoveEngine,
    ImprovementEngine,
    LayoutStrategyEngine,
    VisualStrategyEngine,
    TypographyStrategyEngine,
    ColorStrategyEngine,
    ComponentStrategyEngine,
    MotionStrategyEngine,
    ContentHierarchyEngine,
    PerformanceStrategyEngine,
    AccessibilityStrategyEngine,
    RiskEngine,
    redesign_intelligence_skill,
)

__all__ = [
    # Models
    "RedesignStrategy",
    "PreserveDecision",
    "RemoveDecision",
    "ImproveDecision",
    "LayoutStrategy",
    "VisualStrategy",
    "TypographyStrategy",
    "ColorStrategy",
    "ComponentStrategy",
    "ComponentRecommendation",
    "MotionStrategy",
    "ContentHierarchyStrategy",
    "PerformanceStrategy",
    "AccessibilityStrategy",
    "DesignRisk",
    "ImprovementCategory",
    "LayoutPattern",
    "ComponentAction",
    "Priority",
    # Engines
    "RedesignIntelligenceEngine",
    "PreserveEngine",
    "RemoveEngine",
    "ImprovementEngine",
    "LayoutStrategyEngine",
    "VisualStrategyEngine",
    "TypographyStrategyEngine",
    "ColorStrategyEngine",
    "ComponentStrategyEngine",
    "MotionStrategyEngine",
    "ContentHierarchyEngine",
    "PerformanceStrategyEngine",
    "AccessibilityStrategyEngine",
    "RiskEngine",
    # Skill function
    "redesign_intelligence_skill",
]
