"""
Validation - Plan validation logic
"""
from typing import Dict, List, Tuple, Any
from .models import DesignBuildPlan, ResourceUsage


class PlanValidator:
    """Validates design build plans"""
    
    def validate(self, plan: DesignBuildPlan) -> Tuple[bool, List[str]]:
        """Validate a complete design build plan"""
        errors = []
        warnings = []
        
        # Run all validations
        errors.extend(self._validate_required_fields(plan))
        errors.extend(self._validate_pages(plan))
        errors.extend(self._validate_sections(plan))
        errors.extend(self._validate_components(plan))
        errors.extend(self._validate_design_tokens(plan))
        errors.extend(self._validate_implementation_order(plan))
        errors.extend(self._validate_resource_usage(plan))
        errors.extend(self._validate_responsive_plan(plan))
        errors.extend(self._validate_accessibility_plan(plan))
        errors.extend(self._validate_performance_plan(plan))
        errors.extend(self._validate_motion_plan(plan))
        errors.extend(self._validate_asset_plan(plan))
        
        return len(errors) == 0, errors
    
    def _validate_required_fields(self, plan: DesignBuildPlan) -> List[str]:
        """Validate required fields are present"""
        errors = []
        
        if not plan.project:
            errors.append("Project name is required")
        
        if not plan.framework:
            errors.append("Framework must be specified")
        
        if not plan.styling_system:
            errors.append("Styling system must be specified")
        
        return errors
    
    def _validate_pages(self, plan: DesignBuildPlan) -> List[str]:
        """Validate page plans"""
        errors = []
        
        if not plan.pages:
            errors.append("At least one page plan is required")
        else:
            for i, page in enumerate(plan.pages):
                if not page.route:
                    errors.append(f"Page {i}: route is required")
                if not page.purpose:
                    errors.append(f"Page {i}: purpose is required")
                if not page.sections:
                    errors.append(f"Page {i}: at least one section is required")
        
        return errors
    
    def _validate_sections(self, plan: DesignBuildPlan) -> List[str]:
        """Validate section plans"""
        errors = []
        
        if not plan.sections:
            errors.append("At least one section plan is required")
        else:
            for i, section in enumerate(plan.sections):
                if not section.id:
                    errors.append(f"Section {i}: id is required")
                if not section.name:
                    errors.append(f"Section {i}: name is required")
                if not section.purpose:
                    errors.append(f"Section {i}: purpose is required")
        
        return errors
    
    def _validate_components(self, plan: DesignBuildPlan) -> List[str]:
        """Validate component plans"""
        errors = []
        
        if not plan.components:
            errors.append("At least one component plan is required")
        else:
            for i, component in enumerate(plan.components):
                if not component.id:
                    errors.append(f"Component {i}: id is required")
                if not component.name:
                    errors.append(f"Component {i}: name is required")
                if not component.type:
                    errors.append(f"Component {i}: type is required")
                if not component.purpose:
                    errors.append(f"Component {i}: purpose is required")
        
        return errors
    
    def _validate_design_tokens(self, plan: DesignBuildPlan) -> List[str]:
        """Validate design tokens"""
        errors = []
        
        if not plan.design_tokens:
            errors.append("Design tokens are required")
        elif not plan.design_tokens.colors:
            errors.append("Color tokens are required")
        elif not plan.design_tokens.typography:
            errors.append("Typography tokens are required")
        
        return errors
    
    def _validate_implementation_order(self, plan: DesignBuildPlan) -> List[str]:
        """Validate implementation order"""
        errors = []
        
        if not plan.implementation_order:
            errors.append("Implementation order is required")
        else:
            # Check order is sequential
            for i, step in enumerate(plan.implementation_order):
                expected_order = i + 1
                if step.order != expected_order:
                    errors.append(f"Step {i}: order should be {expected_order}, got {step.order}")
        
        return errors
    
    def _validate_resource_usage(self, plan: DesignBuildPlan) -> List[str]:
        """Validate resource usage decisions"""
        errors = []
        
        if not plan.resource_usage:
            errors.append("Resource usage decisions are required")
        else:
            for i, resource in enumerate(plan.resource_usage):
                if not resource.name:
                    errors.append(f"Resource {i}: name is required")
                if not resource.reason:
                    errors.append(f"Resource {resource.name}: reason is required")
        
        return errors
    
    def _validate_responsive_plan(self, plan: DesignBuildPlan) -> List[str]:
        """Validate responsive plan"""
        errors = []
        
        if not plan.responsive_plan:
            errors.append("Responsive plan is required")
        
        return errors
    
    def _validate_accessibility_plan(self, plan: DesignBuildPlan) -> List[str]:
        """Validate accessibility plan"""
        errors = []
        
        if not plan.accessibility_plan:
            errors.append("Accessibility plan is required")
        elif not plan.accessibility_plan.semantic_html:
            errors.append("Semantic HTML is required for accessibility")
        elif not plan.accessibility_plan.keyboard_navigation:
            errors.append("Keyboard navigation is required for accessibility")
        
        return errors
    
    def _validate_performance_plan(self, plan: DesignBuildPlan) -> List[str]:
        """Validate performance plan"""
        errors = []
        
        if not plan.performance_plan:
            errors.append("Performance plan is required")
        
        return errors
    
    def _validate_motion_plan(self, plan: DesignBuildPlan) -> List[str]:
        """Validate motion plan structure (can be empty)"""
        errors = []
        
        # Motion plan can be empty if no animations needed
        for i, motion in enumerate(plan.motion_plan):
            if not motion.target:
                errors.append(f"Motion {i}: target is required")
            if not motion.trigger:
                errors.append(f"Motion {i}: trigger is required")
            if not motion.type:
                errors.append(f"Motion {i}: type is required")
        
        return errors
    
    def _validate_asset_plan(self, plan: DesignBuildPlan) -> List[str]:
        """Validate asset plan"""
        errors = []
        
        # Asset plan can be empty if no custom assets needed
        for i, asset in enumerate(plan.asset_plan):
            if not asset.id:
                errors.append(f"Asset {i}: id is required")
            if not asset.type:
                errors.append(f"Asset {i}: type is required")
            if not asset.purpose:
                errors.append(f"Asset {i}: purpose is required")
        
        return errors
    
    def validate_quality_gates(self, plan: DesignBuildPlan) -> Tuple[bool, List[str]]:
        """Validate quality gates before Site Builder can begin"""
        errors = []
        
        # Gate 1: DesignBuildPlan valid
        is_valid, validation_errors = self.validate(plan)
        if not is_valid:
            errors.extend(validation_errors)
        
        # Gate 2: No unnecessary dependencies
        for resource in plan.resource_usage:
            if not resource.enabled and resource.name in ["gsap", "lenis", "three.js"]:
                pass  # Good - not using unnecessary deps
            elif resource.enabled and not resource.reason:
                errors.append(f"Resource {resource.name} enabled without justification")
        
        # Gate 3: Responsive defined
        if not plan.responsive_plan:
            errors.append("Quality Gate: Responsive plan not defined")
        
        # Gate 4: Accessibility defined
        if not plan.accessibility_plan:
            errors.append("Quality Gate: Accessibility plan not defined")
        
        # Gate 5: Performance defined
        if not plan.performance_plan:
            errors.append("Quality Gate: Performance plan not defined")
        
        # Gate 6: Assets defined
        # (can be empty list, just needs to exist)
        
        # Gate 7: Motion defined
        # (can be empty list, just needs to exist)
        
        # Gate 8: Implementation order defined
        if not plan.implementation_order:
            errors.append("Quality Gate: Implementation order not defined")
        
        # Gate 9: Resource decisions justified
        for resource in plan.resource_usage:
            if not resource.reason:
                errors.append(f"Quality Gate: Resource {resource.name} lacks justification")
        
        return len(errors) == 0, errors
