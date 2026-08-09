"""
Website Intelligence Engine V0.1

Analyzes website projects to extract design profiles, technology stacks,
and architectural patterns.
"""

from .models import (
    WebsiteDesignProfile,
    TechnologyStack,
    VisualDesign,
    Typography,
    Layout,
    ComponentLibrary,
    AccessibilityInfo,
    PerformanceMetrics,
    AIQualityScore
)
from .inspector import WebsiteInspector
from .analyzers import (
    TechnologyAnalyzer,
    ArchitectureAnalyzer,
    VisualAnalyzer,
    TypographyAnalyzer,
    LayoutAnalyzer,
    ComponentsAnalyzer,
    PatternsAnalyzer,
    MotionAnalyzer,
    AssetsAnalyzer,
    AccessibilityAnalyzer,
    PerformanceAnalyzer,
    AIQualityAnalyzer
)
from .extractors import (
    SourceExtractor,
    CSSExtractor,
    AssetExtractor
)
from .rules import (
    TechnologyRules,
    DesignRules,
    AccessibilityRules,
    PerformanceRules,
    AIQualityRules
)

__all__ = [
    # Models
    'WebsiteDesignProfile',
    'TechnologyStack',
    'VisualDesign',
    'Typography',
    'Layout',
    'ComponentLibrary',
    'AccessibilityInfo',
    'PerformanceMetrics',
    'AIQualityScore',
    # Inspector
    'WebsiteInspector',
    # Analyzers
    'TechnologyAnalyzer',
    'ArchitectureAnalyzer',
    'VisualAnalyzer',
    'TypographyAnalyzer',
    'LayoutAnalyzer',
    'ComponentsAnalyzer',
    'PatternsAnalyzer',
    'MotionAnalyzer',
    'AssetsAnalyzer',
    'AccessibilityAnalyzer',
    'PerformanceAnalyzer',
    'AIQualityAnalyzer',
    # Extractors
    'SourceExtractor',
    'CSSExtractor',
    'AssetExtractor',
    # Rules
    'TechnologyRules',
    'DesignRules',
    'AccessibilityRules',
    'PerformanceRules',
    'AIQualityRules',
]
