"""
Resource Selector - Select and reject resources based on research
"""
from typing import Dict, List, Any, Optional, Tuple
from .models import (
    DesignResourceResearchRequest,
    DesignResource,
    ResourceDecision,
    DesignInspiration,
    DesignResourceReport,
)
from .catalog import DesignResourceCatalog
from .researcher import DesignResourceResearcher
from .rules import ResourceSelectionRules


class ResourceSelector:
    """Selects and rejects resources based on project requirements"""

    def __init__(self, catalog: Optional[DesignResourceCatalog] = None):
        self.catalog = catalog or DesignResourceCatalog()
        self.researcher = DesignResourceResearcher(catalog)
        self.rules = ResourceSelectionRules()

    def select_resources(
        self,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[ResourceDecision], List[ResourceDecision]]:
        """
        Select resources for the project.
        
        Returns:
            Tuple of (selected_resources, rejected_resources)
        """
        # First, get research recommendations
        research_result = self.researcher.research(request)
        resources_to_consult = research_result["resources_to_consult"]

        selected = []
        rejected = []

        # Evaluate each recommended resource
        for resource_id in resources_to_consult:
            resource = self.catalog.get_resource(resource_id)
            if not resource:
                continue

            decision = self.rules.evaluate_resource(resource, request, context)
            
            if decision.selected:
                selected.append(decision)
            else:
                rejected.append(decision)

        # Also evaluate high-priority resources that might not be in the initial list
        high_priority = self.catalog.get_resources_by_priority("VERY HIGH")
        for resource in high_priority:
            if resource.id not in resources_to_consult:
                decision = self.rules.evaluate_resource(resource, request, context)
                if decision.selected and decision.score >= 0.75:
                    selected.append(decision)

        return selected, rejected

    def generate_report(
        self,
        request: DesignResourceResearchRequest,
        task_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DesignResourceReport:
        """Generate a comprehensive design resource report"""
        
        # Get research results
        research_result = self.researcher.research(request)
        
        # Select and reject resources
        selected, rejected = self.select_resources(request, context)
        
        # Extract patterns from selected resources
        patterns_found = []
        animation_ideas = []
        layout_ideas = []
        component_ideas = []
        
        for decision in selected:
            resource_patterns = self.researcher.extract_patterns(
                decision.resource.id,
                {"project_type": request.project_type}
            )
            
            for pattern in resource_patterns:
                patterns_found.append(pattern)
                
                # Categorize ideas
                if "animation" in pattern.pattern.lower() or "motion" in pattern.description.lower():
                    animation_ideas.append(pattern)
                elif "layout" in pattern.pattern.lower() or "grid" in pattern.pattern.lower():
                    layout_ideas.append(pattern)
                else:
                    component_ideas.append(pattern)

        # Build minimum sufficient stack
        minimum_stack = self._build_minimum_stack(selected, request)

        # Generate implementation recommendations
        implementation_recommendations = self._generate_implementation_recommendations(
            selected, request
        )

        # Generate notes
        performance_notes = self._generate_performance_notes(selected, request)
        accessibility_notes = self._generate_accessibility_notes(selected, request)
        license_notes = self._generate_license_notes(selected)
        design_diversity_notes = self._generate_design_diversity_notes(patterns_found)

        # Calculate confidence
        confidence = self._calculate_confidence(selected, patterns_found)

        return DesignResourceReport(
            task_id=task_id,
            project_analysis={
                "project_type": request.project_type,
                "industry": request.industry,
                "brand_personality": request.brand_personality,
                "visual_style": request.visual_style,
                "animation_level": request.animation_level,
                "interaction_level": request.interaction_level,
                "_3d_required": request._3d_required,
            },
            resources_consulted=research_result["resources_to_consult"],
            resources_selected=selected,
            resources_rejected=rejected,
            patterns_found=patterns_found,
            animation_ideas=animation_ideas,
            layout_ideas=layout_ideas,
            component_ideas=component_ideas,
            typography_ideas=[],  # Would be populated with more detailed analysis
            visual_ideas=[],
            asset_ideas=[],
            implementation_recommendations=implementation_recommendations,
            performance_notes=performance_notes,
            accessibility_notes=accessibility_notes,
            license_notes=license_notes,
            design_diversity_notes=design_diversity_notes,
            confidence=confidence,
            minimum_stack=minimum_stack,
        )

    def _build_minimum_stack(
        self,
        selected: List[ResourceDecision],
        request: DesignResourceResearchRequest
    ) -> List[str]:
        """Build the minimum sufficient stack"""
        stack = []
        
        # Always need styling
        styling = next((d for d in selected if d.resource.category.value == "styling"), None)
        if styling:
            stack.append(styling.resource.id)
        else:
            stack.append("tailwind-css")  # Default
        
        # Components based on project type
        components = next((d for d in selected if d.resource.type.value == "component_library"), None)
        if components:
            stack.append(components.resource.id)
        else:
            stack.append("shadcn-ui")  # Default for modern projects
        
        # Animation only if needed
        if request.animation_level in ["MEDIUM", "HIGH"]:
            animation = next((d for d in selected if d.resource.category.value == "animation"), None)
            if animation:
                stack.append(animation.resource.id)
        
        # Icons
        stack.append("lucide")
        
        # Typography
        stack.append("google-fonts")

        return stack

    def _generate_implementation_recommendations(
        self,
        selected: List[ResourceDecision],
        request: DesignResourceResearchRequest
    ) -> List[str]:
        """Generate implementation recommendations"""
        recommendations = []
        
        recommendations.append("Start with Tailwind CSS configuration for design tokens")
        recommendations.append("Set up shadcn/ui components incrementally")
        
        if request.animation_level in ["MEDIUM", "HIGH"]:
            recommendations.append("Implement Motion for page transitions first")
            recommendations.append("Add microinteractions to buttons and links")
        
        if request._3d_required:
            recommendations.append("Create Three.js scene setup early")
            recommendations.append("Optimize 3D assets for web delivery")
        
        recommendations.append("Ensure all components are responsive")
        recommendations.append("Test on mobile devices throughout development")
        
        return recommendations

    def _generate_performance_notes(
        self,
        selected: List[ResourceDecision],
        request: DesignResourceResearchRequest
    ) -> List[str]:
        """Generate performance-related notes"""
        notes = []
        
        if request.performance_priority == "HIGH":
            notes.append("Enable Tailwind CSS purging for production")
            notes.append("Lazy load animation libraries")
            notes.append("Consider code splitting for heavy components")
        
        # Check for heavy resources
        heavy_resources = [d for d in selected if d.performance_cost == "HIGH"]
        if heavy_resources:
            notes.append(f"Heavy resources detected: {[d.resource.name for d in heavy_resources]}")
            notes.append("Monitor bundle size and consider lazy loading")
        
        return notes

    def _generate_accessibility_notes(
        self,
        selected: List[ResourceDecision],
        request: DesignResourceResearchRequest
    ) -> List[str]:
        """Generate accessibility-related notes"""
        notes = []
        
        if request.accessibility_priority == "HIGH":
            notes.append("All interactive elements must have proper focus states")
            notes.append("Ensure color contrast meets WCAG AA standards")
            notes.append("Test with screen readers")
            notes.append("Provide keyboard navigation for all interactions")
        
        # Check accessibility-positive resources
        a11y_resources = [d for d in selected if d.accessibility_impact == "POSITIVE"]
        if a11y_resources:
            notes.append(f"Leveraging accessibility-focused resources: {[d.resource.name for d in a11y_resources]}")
        
        return notes

    def _generate_license_notes(
        self,
        selected: List[ResourceDecision]
    ) -> List[str]:
        """Generate license-related notes"""
        notes = []
        
        for decision in selected:
            if decision.resource.license != "MIT":
                notes.append(f"{decision.resource.name}: {decision.resource.license}")
        
        if not notes:
            notes.append("All selected resources use permissive licenses (MIT)")
        
        return notes

    def _generate_design_diversity_notes(
        self,
        patterns_found: List[DesignInspiration]
    ) -> List[str]:
        """Generate notes about design diversity"""
        notes = []
        
        if len(patterns_found) < 3:
            notes.append("Limited pattern variety - consider exploring additional resources")
        
        # Check for pattern repetition
        pattern_types = set(p.pattern for p in patterns_found)
        if len(pattern_types) < len(patterns_found):
            notes.append("Some pattern repetition detected - ensure visual variety")
        
        notes.append("Adapt patterns to brand identity, do not copy directly")
        notes.append("Combine patterns creatively for unique results")
        
        return notes

    def _calculate_confidence(
        self,
        selected: List[ResourceDecision],
        patterns_found: List[DesignInspiration]
    ) -> float:
        """Calculate overall confidence score"""
        if not selected:
            return 0.3
        
        avg_score = sum(d.score for d in selected) / len(selected)
        pattern_bonus = min(0.2, len(patterns_found) * 0.05)
        
        return min(0.95, avg_score + pattern_bonus)
