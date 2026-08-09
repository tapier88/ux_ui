"""
Resource Selection Rules - Rules for selecting/rejecting resources
"""
from typing import Dict, List, Any, Optional
from .models import DesignResource, DesignResourceResearchRequest, ResourceDecision


class ResourceSelectionRules:
    """Rules for resource selection and rejection"""

    def __init__(self):
        self.rules = {
            "three_js_conditional": self._check_three_js_conditional,
            "minimum_stack": self._check_minimum_stack,
            "performance_over_features": self._check_performance_priority,
            "accessibility_requirement": self._check_accessibility_requirement,
            "avoid_overkill": self._check_avoid_overkill,
        }

    def evaluate_resource(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> ResourceDecision:
        """Evaluate a resource against rules and return a decision"""
        
        score = 0.5
        reasons = []
        selected = False

        # Apply each rule
        for rule_name, rule_func in self.rules.items():
            result = rule_func(resource, request, context)
            if result:
                score += result.get("score_adjustment", 0)
                if result.get("reason"):
                    reasons.append(result["reason"])

        # Determine selection based on score and rules
        if score >= 0.7:
            selected = True
            reasons.append("High fit score")
        elif score <= 0.3:
            selected = False
            reasons.append("Low fit score")
        else:
            # Middle ground - depends on specific needs
            selected = self._make_contextual_decision(resource, request, context)
            reasons.append("Contextual decision")

        return ResourceDecision(
            resource=resource,
            selected=selected,
            score=max(0.0, min(1.0, score)),
            reason="; ".join(reasons),
            complexity=self._assess_complexity(resource),
            performance_cost=self._assess_performance_cost(resource),
            accessibility_impact=self._assess_accessibility_impact(resource),
            visual_fit=self._assess_visual_fit(resource, request),
            project_fit=self._assess_project_fit(resource, request),
            confidence=min(0.9, 0.5 + len(reasons) * 0.1)
        )

    def _check_three_js_conditional(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """CRITICAL RULE: Three.js only if 3D is required"""
        if resource.id == "three-js":
            if not request._3d_required:
                return {
                    "score_adjustment": -0.5,
                    "reason": "Three.js not needed - project does not require 3D/WebGL"
                }
            else:
                return {
                    "score_adjustment": 0.3,
                    "reason": "Three.js appropriate for 3D requirements"
                }
        return None

    def _check_minimum_stack(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Prefer minimum sufficient stack"""
        simple_projects = ["landing_page", "simple_site", "blog"]
        
        if request.project_type in simple_projects:
            heavy_resources = ["gsap", "three-js", "storybook"]
            if resource.id in heavy_resources:
                return {
                    "score_adjustment": -0.2,
                    "reason": "May be overkill for simple project"
                }
        
        return None

    def _check_performance_priority(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Consider performance priority"""
        if request.performance_priority == "HIGH":
            if resource.performance_cost in ["HIGH", "MEDIUM"]:
                return {
                    "score_adjustment": -0.15,
                    "reason": "Performance impact may be concern"
                }
            elif resource.performance_cost == "LOW":
                return {
                    "score_adjustment": 0.1,
                    "reason": "Good performance characteristics"
                }
        return None

    def _check_accessibility_requirement(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Consider accessibility requirements"""
        if request.accessibility_priority == "HIGH":
            impact = self._assess_accessibility_impact(resource)
            if impact == "POSITIVE":
                return {
                    "score_adjustment": 0.2,
                    "reason": "Supports accessibility goals"
                }
            elif impact == "NEGATIVE":
                return {
                    "score_adjustment": -0.3,
                    "reason": "May negatively impact accessibility"
                }
        return None

    def _check_avoid_overkill(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Avoid over-engineering"""
        low_animation = request.animation_level in ["NONE", "LOW"]
        
        if low_animation and resource.category.value == "animation":
            if resource.research_priority == "VERY HIGH":
                return {
                    "score_adjustment": -0.25,
                    "reason": "Advanced animation library not needed for low animation requirements"
                }
        
        return None

    def _make_contextual_decision(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Make contextual decision for borderline cases"""
        # Default logic for edge cases
        if resource.status.value == "PENDING_RESOURCE":
            return False
        
        if resource.research_priority == "VERY HIGH":
            return True
        
        if resource.implementation_priority == "CONDITIONAL":
            # Depends on specific conditions
            return resource.id in context.get("preferred_resources", []) if context else False
        
        return resource.research_priority in ["HIGH", "VERY HIGH"]

    def _assess_complexity(self, resource: DesignResource) -> str:
        """Assess implementation complexity"""
        high_complexity = ["three-js", "gsap", "storybook"]
        medium_complexity = ["react-bits", "magic-ui", "radix-ui"]
        
        if resource.id in high_complexity:
            return "HIGH"
        elif resource.id in medium_complexity:
            return "MEDIUM"
        return "LOW"

    def _assess_performance_cost(self, resource: DesignResource) -> str:
        """Assess performance cost"""
        high_cost = ["three-js", "gsap", "lenis"]
        medium_cost = ["motion", "mui", "ant-design"]
        
        if resource.id in high_cost:
            return "HIGH"
        elif resource.id in medium_cost:
            return "MEDIUM"
        return "LOW"

    def _assess_accessibility_impact(self, resource: DesignResource) -> str:
        """Assess accessibility impact"""
        positive = ["radix-ui", "chakra-ui", "shadcn-ui"]
        negative = ["three-js"]  # Can be problematic if not implemented carefully
        
        if resource.id in positive:
            return "POSITIVE"
        elif resource.id in negative:
            return "NEGATIVE"
        return "NEUTRAL"

    def _assess_visual_fit(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest
    ) -> str:
        """Assess visual style fit"""
        creative_resources = ["react-bits", "magic-ui", "gsap"]
        enterprise_resources = ["mui", "ant-design"]
        
        if request.visual_style in ["creative", "bold", "experimental"]:
            if resource.id in creative_resources:
                return "HIGH"
            elif resource.id in enterprise_resources:
                return "LOW"
        
        if request.visual_style in ["professional", "clean", "minimal"]:
            if resource.id in enterprise_resources:
                return "HIGH"
        
        return "MEDIUM"

    def _assess_project_fit(
        self,
        resource: DesignResource,
        request: DesignResourceResearchRequest
    ) -> str:
        """Assess overall project fit"""
        # Landing pages
        if request.project_type == "landing_page":
            landing_friendly = ["shadcn-ui", "tailwind-css", "motion", "react-bits", "magic-ui"]
            if resource.id in landing_friendly:
                return "HIGH"
        
        # Enterprise
        if request.project_type in ["enterprise", "dashboard"]:
            enterprise_friendly = ["mui", "ant-design", "chakra-ui"]
            if resource.id in enterprise_friendly:
                return "HIGH"
        
        return "MEDIUM"
