"""
Design Resource Researcher - Research design resources based on project needs
"""
from typing import Dict, List, Any, Optional
from .models import (
    DesignResourceResearchRequest,
    DesignResource,
    DesignInspiration,
    ResourceDecision,
)
from .catalog import DesignResourceCatalog
from .rules import ResourceSelectionRules


class DesignResourceResearcher:
    """Researches design resources based on project requirements"""

    def __init__(self, catalog: Optional[DesignResourceCatalog] = None):
        self.catalog = catalog or DesignResourceCatalog()
        self.rules = ResourceSelectionRules()

    def research(self, request: DesignResourceResearchRequest) -> Dict[str, Any]:
        """
        Research resources based on project requirements.
        
        Returns a dictionary with:
        - resources_to_consult: List of resource IDs to investigate
        - priority_resources: High priority resources for this project
        - patterns_to_study: Patterns worth investigating
        - recommendations: Initial recommendations
        """
        resources_to_consult = []
        priority_resources = []
        patterns_to_study = []
        recommendations = []

        # Foundation/Styling - always needed
        if request.visual_style in ["modern", "clean", "minimal"]:
            resources_to_consult.append("tailwind-css")
            priority_resources.append("tailwind-css")
            recommendations.append("Tailwind CSS recommended for modern styling approach")

        # Components based on project type
        if request.project_type in ["landing_page", "saas", "startup"]:
            resources_to_consult.extend(["shadcn-ui", "radix-ui"])
            priority_resources.append("shadcn-ui")
            recommendations.append("shadcn/ui for copy-paste component architecture")

        elif request.project_type in ["enterprise", "dashboard", "admin"]:
            resources_to_consult.extend(["mui", "ant-design"])
            priority_resources.append("mui")
            recommendations.append("MUI or Ant Design for enterprise components")

        # Animation based on animation level
        if request.animation_level == "HIGH":
            resources_to_consult.extend(["motion", "gsap", "lenis"])
            priority_resources.extend(["motion", "gsap"])
            patterns_to_study.extend([
                "scroll-triggered animations",
                "page transitions",
                "microinteractions"
            ])
            recommendations.append("GSAP + Lenis for premium scroll experience")
            recommendations.append("Motion for React-based interactions")

        elif request.animation_level == "MEDIUM":
            resources_to_consult.append("motion")
            priority_resources.append("motion")
            patterns_to_study.extend([
                "fade-in animations",
                "hover effects",
                "button microinteractions"
            ])
            recommendations.append("Motion library for essential animations")

        elif request.animation_level == "LOW":
            resources_to_consult.append("animate-css")
            recommendations.append("Simple CSS animations sufficient")

        # 3D check - CRITICAL RULE
        if request._3d_required:
            resources_to_consult.append("three-js")
            priority_resources.append("three-js")
            recommendations.append("Three.js for 3D/WebGL requirements")
        else:
            # Explicitly DO NOT recommend Three.js if not needed
            recommendations.append("Three.js NOT needed - avoid unnecessary complexity")

        # Creative components for modern/creative projects
        if request.visual_style in ["creative", "bold", "experimental"]:
            resources_to_consult.extend(["react-bits", "magic-ui"])
            priority_resources.extend(["react-bits", "magic-ui"])
            patterns_to_study.extend([
                "animated hero sections",
                "creative layouts",
                "unique interactions"
            ])
            recommendations.append("React Bits for creative pattern inspiration")
            recommendations.append("Magic UI for stunning visual effects")

        # Iconography
        resources_to_consult.append("lucide")
        recommendations.append("Lucide for clean, consistent iconography")

        # Typography
        resources_to_consult.append("google-fonts")
        recommendations.append("Google Fonts for typography options")

        # Asset generation
        if request.asset_generation_required:
            resources_to_consult.append("higgsfield")
            recommendations.append("Higgsfield for AI-powered asset generation")

        # Quality check reminder
        recommendations.append("AI Quality Detector should be used in review phase")

        # Performance considerations
        if request.performance_priority == "HIGH":
            recommendations.append("Prioritize lightweight solutions")
            recommendations.append("Avoid heavy animation libraries if not essential")
            # Remove GSAP from priority if performance is critical and animation is low
            if request.animation_level == "LOW":
                if "gsap" in priority_resources:
                    priority_resources.remove("gsap")

        # Accessibility considerations
        if request.accessibility_priority == "HIGH":
            recommendations.append("Ensure all selected components meet WCAG guidelines")
            recommendations.append("Radix UI provides excellent accessibility primitives")

        return {
            "resources_to_consult": resources_to_consult,
            "priority_resources": priority_resources,
            "patterns_to_study": patterns_to_study,
            "recommendations": recommendations,
            "request": request.to_dict(),
        }

    def get_resource_details(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific resource"""
        resource = self.catalog.get_resource(resource_id)
        if resource:
            return resource.to_dict()
        return None

    def consult_resource(self, resource_id: str) -> Optional[DesignResource]:
        """
        Consult a resource from the catalog.
        This simulates the agent studying the resource.
        """
        return self.catalog.get_resource(resource_id)

    def extract_patterns(self, resource_id: str, context: Dict[str, Any]) -> List[DesignInspiration]:
        """
        Extract design patterns from a resource.
        
        This is where the agent would study the resource and identify:
        - composition patterns
        - interaction patterns
        - animation patterns
        - layout patterns
        """
        resource = self.catalog.get_resource(resource_id)
        if not resource:
            return []

        patterns = []

        # Example pattern extraction based on resource type
        if resource_id == "react-bits":
            patterns.extend([
                DesignInspiration(
                    source=resource_id,
                    resource=resource.name,
                    pattern="animated_hero",
                    description="Hero section with animated elements",
                    why_relevant="Creates engaging first impression",
                    adaptation="Adapt animation timing to brand personality",
                    complexity="MEDIUM",
                    performance="MEDIUM",
                    confidence=0.8
                ),
                DesignInspiration(
                    source=resource_id,
                    resource=resource.name,
                    pattern="interactive_cards",
                    description="Cards with hover/touch interactions",
                    why_relevant="Enhances user engagement",
                    adaptation="Use for feature/product cards",
                    complexity="LOW",
                    performance="HIGH",
                    confidence=0.85
                )
            ])

        elif resource_id == "magic-ui":
            patterns.extend([
                DesignInspiration(
                    source=resource_id,
                    resource=resource.name,
                    pattern="marquee",
                    description="Continuous scrolling content strip",
                    why_relevant="Dynamic way to showcase logos/testimonials",
                    adaptation="Use for client logos or features",
                    complexity="LOW",
                    performance="MEDIUM",
                    confidence=0.75
                ),
                DesignInspiration(
                    source=resource_id,
                    resource=resource.name,
                    pattern="gradient_glow",
                    description="Subtle gradient background effects",
                    why_relevant="Adds visual depth without overwhelming",
                    adaptation="Apply sparingly to key sections",
                    complexity="LOW",
                    performance="HIGH",
                    confidence=0.7
                )
            ])

        elif resource_id == "shadcn-ui":
            patterns.extend([
                DesignInspiration(
                    source=resource_id,
                    resource=resource.name,
                    pattern="bento_grid",
                    description="Grid layout with varied cell sizes",
                    why_relevant="Modern way to present features/content",
                    adaptation="Use for features or pricing sections",
                    complexity="MEDIUM",
                    performance="HIGH",
                    confidence=0.9
                )
            ])

        return patterns

    def validate_resource_fit(self, resource: DesignResource, request: DesignResourceResearchRequest) -> bool:
        """Validate if a resource fits the project requirements"""
        # Check conditional rules
        if resource.id == "three-js" and not request._3d_required:
            return False

        # Check animation level vs resource type
        if resource.type.value == "animation_library":
            if request.animation_level == "NONE":
                return False
            if request.animation_level == "LOW" and resource.research_priority == "VERY HIGH":
                # Might be overkill
                return False

        return True
