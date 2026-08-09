"""
Design Execution Planner - Main orchestration
Converts design decisions into a technical build plan
"""
from typing import Dict, List, Optional, Any
from .models import (
    DesignBuildPlan, PagePlan, SectionPlan, ComponentPlan,
    LayoutType, ResourceUsage, ImplementationStep, FilePlan,
    MigrationPlan, MigrationItem, CodeAction, DesignTokens,
    ColorTokens, TypographyTokens, SpacingTokens
)
from .component_planner import ComponentPlanner
from .layout_planner import LayoutPlanner
from .motion_planner import MotionPlanner
from .asset_planner import AssetPlanner
from .responsive_planner import ResponsivePlanner
from .accessibility_planner import AccessibilityPlanner
from .performance_planner import PerformancePlanner
from .validation import PlanValidator


class DesignExecutionPlanner:
    """Main orchestrator for design execution planning"""
    
    def __init__(self):
        self.component_planner = ComponentPlanner()
        self.layout_planner = LayoutPlanner()
        self.motion_planner = MotionPlanner()
        self.asset_planner = AssetPlanner()
        self.responsive_planner = ResponsivePlanner()
        self.accessibility_planner = AccessibilityPlanner()
        self.performance_planner = PerformancePlanner()
        self.validator = PlanValidator()
    
    def create_build_plan(
        self,
        project_name: str,
        design_profile: Optional[Dict[str, Any]] = None,
        redesign_strategy: Optional[Dict[str, Any]] = None,
        resource_report: Optional[Dict[str, Any]] = None,
        existing_code: Optional[Dict[str, Any]] = None
    ) -> DesignBuildPlan:
        """Create a complete design build plan"""
        
        # Initialize plan with basic configuration
        plan = DesignBuildPlan(project=project_name)
        
        # Apply design profile settings
        if design_profile:
            self._apply_design_profile(plan, design_profile)
        
        # Apply redesign strategy
        if redesign_strategy:
            self._apply_redesign_strategy(plan, redesign_strategy)
        
        # Apply resource report decisions
        if resource_report:
            self._apply_resource_report(plan, resource_report)
        
        # Handle existing code awareness
        if existing_code:
            self._handle_existing_code(plan, existing_code)
        
        # Generate pages
        self._generate_pages(plan, design_profile, redesign_strategy)
        
        # Generate sections
        self._generate_sections(plan, design_profile, redesign_strategy)
        
        # Generate components
        self._generate_components(plan, design_profile, resource_report)
        
        # Generate layout plan
        plan.layout_plan = self.layout_planner.plan_layout(
            layout_type=self._determine_layout_type(design_profile)
        )
        
        # Generate design tokens
        plan.design_tokens = self._generate_design_tokens(design_profile)
        plan.typography_plan = plan.design_tokens.typography
        plan.color_plan = plan.design_tokens.colors
        plan.spacing_plan = plan.design_tokens.spacing
        
        # Generate asset plan
        if resource_report:
            plan.asset_plan = self.asset_planner.from_design_resource_report(resource_report)
        else:
            plan.asset_plan = [self.asset_planner.plan_hero_image()]
        
        # Generate motion plan
        plan.motion_plan = self._generate_motion_plan(design_profile, resource_report)
        
        # Generate responsive plan
        plan.responsive_plan = self.responsive_planner.plan_standard_responsive()
        
        # Generate accessibility plan
        plan.accessibility_plan = self.accessibility_planner.plan_wcag_aa()
        
        # Generate performance plan
        plan.performance_plan = self.performance_planner.plan_standard()
        
        # Generate implementation order
        plan.implementation_order = self._generate_implementation_order()
        
        # Generate file plan
        plan.file_plan = self._generate_file_plan()
        
        # Generate resource usage
        plan.resource_usage = self._generate_resource_usage(resource_report)
        
        # Generate validation plan
        plan.validation_plan = self._generate_validation_plan()
        
        return plan
    
    def _apply_design_profile(self, plan: DesignBuildPlan, profile: Dict[str, Any]):
        """Apply design profile settings to the plan"""
        branding = profile.get("branding", {})
        colors = branding.get("colors", {})
        
        if colors:
            plan.color_plan.primary = colors.get("primary", plan.color_plan.primary)
            plan.color_plan.secondary = colors.get("secondary", plan.color_plan.secondary)
            plan.color_plan.accent = colors.get("accent", plan.color_plan.accent)
        
        typography = profile.get("typography", {})
        if typography:
            plan.typography_plan.font_family = typography.get("font_family", plan.typography_plan.font_family)
    
    def _apply_redesign_strategy(self, plan: DesignBuildPlan, strategy: Dict[str, Any]):
        """Apply redesign strategy to the plan"""
        # Strategy can influence layout types, component choices, etc.
        pass
    
    def _apply_resource_report(self, plan: DesignBuildPlan, report: Dict[str, Any]):
        """Apply resource report decisions"""
        # Resources determine which libraries will be used
        pass
    
    def _handle_existing_code(self, plan: DesignBuildPlan, existing: Dict[str, Any]):
        """Handle existing code awareness and migration"""
        files = existing.get("files", [])
        plan.migration_plan = MigrationPlan()
        
        for file_info in files:
            path = file_info.get("path", "")
            action_str = file_info.get("action", "preserve")
            action = getattr(CodeAction, action_str.upper(), CodeAction.PRESERVE)
            
            item = MigrationItem(
                path=path,
                action=action,
                reason=file_info.get("reason", "Preserve existing functionality"),
                risk=file_info.get("risk", "low")
            )
            
            if action == CodeAction.PRESERVE:
                plan.migration_plan.preserve.append(item)
            elif action == CodeAction.MODIFY:
                plan.migration_plan.modify.append(item)
            elif action == CodeAction.REPLACE:
                plan.migration_plan.replace.append(item)
            elif action == CodeAction.REMOVE:
                plan.migration_plan.remove.append(item)
            elif action == CodeAction.CREATE:
                plan.migration_plan.create.append(item)
    
    def _determine_layout_type(self, design_profile: Optional[Dict[str, Any]]) -> LayoutType:
        """Determine layout type from design profile"""
        if not design_profile:
            return LayoutType.STANDARD
        
        style = design_profile.get("style", "standard")
        layout_map = {
            "minimal": LayoutType.CENTERED,
            "bold": LayoutType.FULL_BLEED,
            "editorial": LayoutType.EDITORIAL,
            "creative": LayoutType.ASYMMETRIC,
            "immersive": LayoutType.IMMERSIVE,
            "storytelling": LayoutType.STORYTELLING
        }
        return layout_map.get(style, LayoutType.STANDARD)
    
    def _generate_pages(
        self,
        plan: DesignBuildPlan,
        design_profile: Optional[Dict[str, Any]],
        redesign_strategy: Optional[Dict[str, Any]]
    ):
        """Generate page plans"""
        # Default home page
        home_page = PagePlan(
            route="/",
            purpose="Homepage - Main landing page",
            sections=["hero", "trust", "benefits", "product", "testimonials", "cta", "footer"],
            primary_cta="Get Started",
            secondary_cta="Learn More",
            navigation="main",
            footer="main",
            seo_requirements={
                "title": "Home",
                "description": "Welcome to our site",
                "og_image": True
            }
        )
        plan.pages.append(home_page)
    
    def _generate_sections(
        self,
        plan: DesignBuildPlan,
        design_profile: Optional[Dict[str, Any]],
        redesign_strategy: Optional[Dict[str, Any]]
    ):
        """Generate section plans"""
        layout_type = self._determine_layout_type(design_profile)
        
        # Hero section
        hero = SectionPlan(
            id="hero",
            name="Hero",
            purpose="Above the fold content with primary CTA",
            layout=layout_type,
            components=["headline", "subheadline", "cta-button", "hero-image"],
            background={"type": "gradient"},
            motion=["fade-in", "slide-up"],
            responsive_behavior={"mobile": "stack"},
            accessibility={"heading_level": 1},
            performance_priority="critical"
        )
        plan.sections.append(hero)
        
        # Trust section
        trust = SectionPlan(
            id="trust",
            name="Trust Indicators",
            purpose="Social proof and credibility",
            layout=LayoutType.CENTERED,
            components=["logo-grid", "stats"],
            performance_priority="high"
        )
        plan.sections.append(trust)
        
        # Benefits section
        benefits = SectionPlan(
            id="benefits",
            name="Benefits",
            purpose="Key value propositions",
            layout=LayoutType.GRID,
            components=["feature-cards"],
            performance_priority="normal"
        )
        plan.sections.append(benefits)
    
    def _generate_components(
        self,
        plan: DesignBuildPlan,
        design_profile: Optional[Dict[str, Any]],
        resource_report: Optional[Dict[str, Any]]
    ):
        """Generate component plans"""
        # Button component
        button = self.component_planner.plan_button(
            variant="primary",
            purpose="Primary user actions"
        )
        plan.components.append(button)
        
        # Card component
        card = self.component_planner.plan_card(
            purpose="Content containers"
        )
        plan.components.append(card)
        
        # Navigation component
        nav = self.component_planner.plan_navigation(
            purpose="Site navigation"
        )
        plan.components.append(nav)
    
    def _generate_design_tokens(self, design_profile: Optional[Dict[str, Any]]) -> DesignTokens:
        """Generate design tokens"""
        tokens = DesignTokens()
        
        if design_profile:
            branding = design_profile.get("branding", {})
            colors = branding.get("colors", {})
            
            if colors.get("primary"):
                tokens.colors.primary = colors["primary"]
            if colors.get("secondary"):
                tokens.colors.secondary = colors["secondary"]
            if colors.get("accent"):
                tokens.colors.accent = colors["accent"]
        
        return tokens
    
    def _generate_motion_plan(
        self,
        design_profile: Optional[Dict[str, Any]],
        resource_report: Optional[Dict[str, Any]]
    ) -> List:
        """Generate motion plans"""
        motions = []
        
        # Hero fade in
        hero_motion = self.motion_planner.plan_fade_in(
            target="#hero",
            trigger="load",
            duration="600ms"
        )
        motions.append(hero_motion)
        
        return motions
    
    def _generate_implementation_order(self) -> List[ImplementationStep]:
        """Generate implementation order"""
        return [
            ImplementationStep(order=1, task="Project setup", files=["package.json", "tsconfig.json"]),
            ImplementationStep(order=2, task="Design tokens", files=["src/tokens/"]),
            ImplementationStep(order=3, task="Typography", files=["src/styles/typography.css"]),
            ImplementationStep(order=4, task="Global layout", files=["src/layouts/"]),
            ImplementationStep(order=5, task="Navigation", components=["Navigation"]),
            ImplementationStep(order=6, task="Hero section", components=["Hero"]),
            ImplementationStep(order=7, task="Content sections", components=["Benefits", "Features"]),
            ImplementationStep(order=8, task="Interactions", files=["src/animations/"]),
            ImplementationStep(order=9, task="Responsive adaptations"),
            ImplementationStep(order=10, task="Accessibility audit"),
            ImplementationStep(order=11, task="Performance optimization"),
            ImplementationStep(order=12, task="Quality validation", validation=["tests", "lighthouse"])
        ]
    
    def _generate_file_plan(self) -> List[FilePlan]:
        """Generate file structure plan"""
        return [
            FilePlan(path="src/", type="directory", purpose="Source code"),
            FilePlan(path="src/components/", type="directory", purpose="Reusable components", components=["Button", "Card"]),
            FilePlan(path="src/sections/", type="directory", purpose="Page sections", components=["Hero", "Benefits"]),
            FilePlan(path="src/layouts/", type="directory", purpose="Layout components"),
            FilePlan(path="src/styles/", type="directory", purpose="Global styles"),
            FilePlan(path="src/hooks/", type="directory", purpose="Custom React hooks"),
            FilePlan(path="src/animations/", type="directory", purpose="Animation definitions"),
            FilePlan(path="src/assets/", type="directory", purpose="Static assets")
        ]
    
    def _generate_resource_usage(self, resource_report: Optional[Dict[str, Any]]) -> List[ResourceUsage]:
        """Generate resource usage decisions"""
        usages = [
            ResourceUsage(name="tailwind", enabled=True, reason="Primary styling system"),
            ResourceUsage(name="shadcn", enabled=True, reason="Component library base"),
            ResourceUsage(name="motion", enabled=True, reason="Animation library"),
            ResourceUsage(name="gsap", enabled=False, reason="Not needed for current animation requirements"),
            ResourceUsage(name="lenis", enabled=False, reason="Native scroll sufficient"),
            ResourceUsage(name="three.js", enabled=False, reason="No 3D requirements"),
            ResourceUsage(name="react-bits", enabled=True, reason="Selected interactive patterns")
        ]
        
        if resource_report:
            # Adjust based on resource report
            pass
        
        return usages
    
    def _generate_validation_plan(self) -> List[str]:
        """Generate validation plan"""
        return [
            "Validate DesignBuildPlan structure",
            "Verify all required fields present",
            "Check resource usage justifications",
            "Validate responsive breakpoints defined",
            "Verify accessibility requirements met",
            "Check performance budgets defined",
            "Validate implementation order is logical",
            "Verify file paths are consistent"
        ]
    
    def validate_plan(self, plan: DesignBuildPlan) -> tuple[bool, List[str]]:
        """Validate a design build plan"""
        return self.validator.validate(plan)
    
    def validate_quality_gates(self, plan: DesignBuildPlan) -> tuple[bool, List[str]]:
        """Validate quality gates before Site Builder can begin"""
        return self.validator.validate_quality_gates(plan)
