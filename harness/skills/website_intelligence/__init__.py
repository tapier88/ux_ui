"""
Website Intelligence - Skill module for website design analysis
"""
from typing import Dict, Any, Optional

from .models import (
    WebsiteDesignProfile,
    TechnologyStack,
    VisualDesign,
    Typography,
    Layout,
    ComponentLibrary,
    AccessibilityInfo,
    PerformanceMetrics,
    AIQualityScore,
    DesignStyle,
    ColorPalette,
    ColorPaletteType,
    ColorInfo
)
from .inspector import WebsiteInspector


def analyze_website(project_path: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a website and return its design profile.
    
    Args:
        project_path: Path to local project directory
        url: URL of remote website
        
    Returns:
        Dictionary containing the website design profile
    """
    inspector = WebsiteInspector(project_path=project_path)
    profile = inspector.inspect(url=url)
    return profile.to_dict()


def create_design_profile(project_name: str = "unknown") -> WebsiteDesignProfile:
    """
    Create a new empty design profile.
    
    Args:
        project_name: Name of the project
        
    Returns:
        New WebsiteDesignProfile instance
    """
    return WebsiteDesignProfile(project_name=project_name)


def register_website_intelligence_skill(registry):
    """
    Register the website intelligence skill with a registry.
    
    Args:
        registry: Skill registry instance
    """
    registry.register_skill(
        name="website-intelligence",
        description="Analyze website design, technology stack, and quality metrics",
        func=analyze_website,
        category="analysis",
        version="1.0.0"
    )


# Export all public classes
__all__ = [
    'WebsiteDesignProfile',
    'TechnologyStack',
    'VisualDesign',
    'Typography',
    'Layout',
    'ComponentLibrary',
    'AccessibilityInfo',
    'PerformanceMetrics',
    'AIQualityScore',
    'DesignStyle',
    'ColorPalette',
    'ColorPaletteType',
    'ColorInfo',
    'WebsiteInspector',
    'analyze_website',
    'create_design_profile',
    'register_website_intelligence_skill'
]
