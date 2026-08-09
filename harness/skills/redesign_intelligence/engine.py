"""
Redesign Intelligence Engine

This engine analyzes a WebsiteDesignProfile and produces a comprehensive
RedesignStrategy including preserve, remove, improve decisions and strategies
for layout, visual design, typography, color, components, motion, accessibility,
and performance.
"""

from typing import Dict, Any, List, Optional
import random

from .models import (
    PreserveDecision,
    RemoveDecision,
    ImproveDecision,
    LayoutStrategy,
    VisualStrategy,
    TypographyStrategy,
    ColorStrategy,
    ComponentStrategy,
    MotionStrategy,
    ContentHierarchyStrategy,
    PerformanceStrategy,
    AccessibilityStrategy,
    DesignRisk,
    RedesignStrategy,
)


# Layout patterns for diversity
LAYOUT_PATTERNS = [
    "asymmetric",
    "editorial",
    "bento",
    "centered",
    "overlapping",
    "immersive",
    "split",
    "diagonal",
    "layered",
    "full-bleed",
    "storytelling",
    "grid",
    "experimental",
]

# Industry-specific layout preferences
INDUSTRY_LAYOUT_PREFS = {
    "technology": ["asymmetric", "immersive", "experimental", "bento"],
    "creative": ["editorial", "overlapping", "diagonal", "layered"],
    "corporate": ["grid", "split", "centered", "bento"],
    "ecommerce": ["bento", "grid", "split", "centered"],
    "portfolio": ["editorial", "full-bleed", "storytelling", "overlapping"],
    "saas": ["asymmetric", "bento", "split", "centered"],
    "healthcare": ["centered", "grid", "split", "bento"],
    "finance": ["grid", "split", "centered", "bento"],
    "education": ["grid", "centered", "storytelling", "split"],
    "entertainment": ["immersive", "full-bleed", "overlapping", "experimental"],
}

# Brand personality to layout mapping
BRAND_PERSONALITY_LAYOUTS = {
    "modern": ["asymmetric", "experimental", "bento", "overlapping"],
    "traditional": ["grid", "centered", "split"],
    "playful": ["diagonal", "layered", "overlapping", "experimental"],
    "professional": ["grid", "split", "centered", "bento"],
    "bold": ["full-bleed", "immersive", "diagonal", "experimental"],
    "minimal": ["centered", "grid", "split", "bento"],
    "elegant": ["editorial", "layered", "asymmetric"],
    "innovative": ["experimental", "asymmetric", "overlapping", "diagonal"],
}


class PreserveEngine:
    """Determines what elements to preserve from the original design"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[PreserveDecision]:
        decisions = []
        
        # Check for brand identity elements
        brand = profile.get("brand", {})
        if brand.get("logo") or brand.get("name"):
            decisions.append(PreserveDecision(
                element="brand_identity",
                reason="Brand identity is core to recognition and should be maintained",
                confidence=0.95,
            ))
        
        # Check for value proposition
        content = profile.get("content", {})
        if content.get("value_proposition"):
            decisions.append(PreserveDecision(
                element="value_proposition",
                reason="Core value proposition drives conversion and should be preserved",
                confidence=0.90,
            ))
        
        # Check for navigation structure
        navigation = profile.get("navigation", {})
        if navigation.get("items"):
            decisions.append(PreserveDecision(
                element="navigation_structure",
                reason="Existing navigation may have established user mental models",
                confidence=0.75,
            ))
        
        # Check for SEO-critical content
        seo = profile.get("seo", {})
        if seo.get("keywords") or seo.get("meta_description"):
            decisions.append(PreserveDecision(
                element="seo_structure",
                reason="SEO elements are critical for search visibility",
                confidence=0.85,
            ))
        
        # Check for accessible components
        accessibility = profile.get("accessibility", {})
        if accessibility.get("compliant_elements"):
            decisions.append(PreserveDecision(
                element="accessible_components",
                reason="Components with good accessibility should be maintained",
                confidence=0.80,
            ))
        
        # Check for functional components
        components = profile.get("components", {})
        if components.get("forms") or components.get("interactive_elements"):
            decisions.append(PreserveDecision(
                element="functional_components",
                reason="Working functional components provide user value",
                confidence=0.70,
            ))
        
        # Default preservation if nothing specific found
        if not decisions:
            decisions.append(PreserveDecision(
                element="core_content",
                reason="Essential content and functionality should be preserved by default",
                confidence=0.60,
            ))
        
        return decisions


class RemoveEngine:
    """Determines what elements to remove from the original design"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[RemoveDecision]:
        decisions = []
        
        visual = profile.get("visual", {})
        
        # Check for excessive shadows
        if visual.get("shadows") == "heavy" or visual.get("shadow_count", 0) > 5:
            decisions.append(RemoveDecision(
                element="excessive_shadows",
                reason="Heavy shadows create visual noise and reduce clarity",
                confidence=0.75,
            ))
        
        # Check for arbitrary gradients
        if visual.get("gradients") == "excessive" or visual.get("gradient_count", 0) > 3:
            decisions.append(RemoveDecision(
                element="arbitrary_gradients",
                reason="Excessive gradients can appear dated and distract from content",
                confidence=0.70,
            ))
        
        # Check for unnecessary animations
        motion = profile.get("motion", {})
        if motion.get("animation_count", 0) > 10 or motion.get("intensity") == "high":
            decisions.append(RemoveDecision(
                element="unnecessary_animations",
                reason="Too many animations can hurt performance and distract users",
                confidence=0.80,
            ))
        
        # Check for redundant content
        content = profile.get("content", {})
        sections = content.get("sections", [])
        if len(sections) > 10:
            decisions.append(RemoveDecision(
                element="redundant_sections",
                reason="Too many sections dilute message impact and overwhelm users",
                confidence=0.65,
            ))
        
        # Check for decorative elements without purpose
        if visual.get("decorative_elements", 0) > 5:
            decisions.append(RemoveDecision(
                element="purposeless_decoration",
                reason="Decorative elements without functional purpose add cognitive load",
                confidence=0.60,
            ))
        
        # Check for generic UI patterns
        components = profile.get("components", {})
        if components.get("generic_patterns", False):
            decisions.append(RemoveDecision(
                element="generic_ui_patterns",
                reason="Generic UI patterns reduce brand differentiation",
                confidence=0.55,
            ))
        
        # Default removal suggestions if nothing specific
        if not decisions:
            decisions.append(RemoveDecision(
                element="visual_clutter",
                reason="Removing unnecessary visual elements improves focus",
                confidence=0.50,
            ))
        
        return decisions


class ImprovementEngine:
    """Detects opportunities for improvement"""
    
    CATEGORIES = ["visual", "layout", "typography", "content", "conversion", 
                  "accessibility", "performance", "interaction", "responsive"]
    
    def analyze(self, profile: Dict[str, Any]) -> List[ImproveDecision]:
        improvements = []
        
        # Visual improvements
        visual = profile.get("visual", {})
        if visual.get("density") == "high":
            improvements.append(ImproveDecision(
                category="visual",
                current_state="High visual density throughout the design",
                problem="Content feels cramped and overwhelming",
                proposed_change="Increase negative space between sections and elements",
                expected_benefit="Improved readability and reduced cognitive load",
                priority="high",
                confidence=0.85,
            ))
        
        # Layout improvements
        layout = profile.get("layout", {})
        if layout.get("pattern") == "traditional_hero":
            improvements.append(ImproveDecision(
                category="layout",
                current_state="Traditional hero with text-left/image-right pattern",
                problem="Predictable layout fails to capture attention",
                proposed_change="Consider asymmetric or editorial layout for uniqueness",
                expected_benefit="Increased engagement and brand memorability",
                priority="medium",
                confidence=0.70,
            ))
        
        # Typography improvements
        typography = profile.get("typography", {})
        if not typography.get("hierarchy"):
            improvements.append(ImproveDecision(
                category="typography",
                current_state="Unclear typographic hierarchy",
                problem="Users struggle to identify important content",
                proposed_change="Establish clear H1/H2/H3 hierarchy with distinct sizes and weights",
                expected_benefit="Better content scanning and comprehension",
                priority="high",
                confidence=0.90,
            ))
        
        # Accessibility improvements
        accessibility = profile.get("accessibility", {})
        if accessibility.get("contrast_ratio", 4.5) < 4.5:
            improvements.append(ImproveDecision(
                category="accessibility",
                current_state=f"Color contrast ratio below WCAG AA standard ({accessibility.get('contrast_ratio', 'unknown')})",
                problem="Text may be difficult to read for users with visual impairments",
                proposed_change="Increase contrast ratio to minimum 4.5:1 for normal text",
                expected_benefit="Improved accessibility and legal compliance",
                priority="critical",
                confidence=0.95,
            ))
        
        # Performance improvements
        performance = profile.get("performance", {})
        if performance.get("image_sizes") == "unoptimized":
            improvements.append(ImproveDecision(
                category="performance",
                current_state="Images not optimized for web",
                problem="Slow page load times affecting user experience and SEO",
                proposed_change="Implement responsive images with WebP format and lazy loading",
                expected_benefit="Faster load times and improved Core Web Vitals",
                priority="high",
                confidence=0.85,
            ))
        
        # Content improvements
        content = profile.get("content", {})
        if len(content.get("sections", [])) > 8:
            improvements.append(ImproveDecision(
                category="content",
                current_state="Excessive content sections",
                problem="Message dilution and user fatigue",
                proposed_change="Consolidate related sections and prioritize key messages",
                expected_benefit="Clearer value proposition and higher conversion",
                priority="medium",
                confidence=0.75,
            ))
        
        # Default improvement if nothing specific found
        if not improvements:
            improvements.append(ImproveDecision(
                category="visual",
                current_state="Standard visual treatment",
                problem="Design lacks distinctive character",
                proposed_change="Introduce unique visual elements aligned with brand personality",
                expected_benefit="Increased brand recognition and memorability",
                priority="medium",
                confidence=0.60,
            ))
        
        return improvements


class LayoutStrategyEngine:
    """Generates layout strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> LayoutStrategy:
        industry = profile.get("industry", "general").lower()
        brand_personality = profile.get("brand", {}).get("personality", "modern").lower()
        content_type = profile.get("content_type", "standard")
        
        # Select layout based on industry and brand
        industry_prefs = INDUSTRY_LAYOUT_PREFS.get(industry, LAYOUT_PATTERNS[:4])
        brand_prefs = BRAND_PERSONALITY_LAYOUTS.get(brand_personality, LAYOUT_PATTERNS[:4])
        
        # Find intersection or use weighted selection
        common = set(industry_prefs) & set(brand_prefs)
        if common:
            selected_pattern = list(common)[0]
        else:
            # Weighted selection favoring industry
            candidates = industry_prefs + brand_prefs
            selected_pattern = random.choice(candidates[:len(candidates)//2])
        
        descriptions = {
            "asymmetric": "Asymmetric layout creates dynamic tension and visual interest",
            "editorial": "Editorial layout mimics magazine spreads for sophisticated storytelling",
            "bento": "Bento grid organizes content in modular, scannable blocks",
            "centered": "Centered layout provides balance and focuses attention",
            "overlapping": "Overlapping elements create depth and layered composition",
            "immersive": "Immersive layout uses full viewport for maximum impact",
            "split": "Split layout divides screen for clear content separation",
            "diagonal": "Diagonal composition adds energy and guides eye movement",
            "layered": "Layered design creates depth through z-axis positioning",
            "full-bleed": "Full-bleed imagery extends to edges for dramatic effect",
            "storytelling": "Storytelling layout sequences content narratively",
            "grid": "Grid system provides structure and consistency",
            "experimental": "Experimental layout breaks conventions for uniqueness",
        }
        
        reasoning = f"Selected based on {industry} industry standards and {brand_personality} brand personality"
        
        return LayoutStrategy(
            pattern=selected_pattern,
            description=descriptions.get(selected_pattern, "Custom layout approach"),
            reasoning=reasoning,
            sections=self._generate_sections(profile, selected_pattern),
        )
    
    def _generate_sections(self, profile: Dict[str, Any], pattern: str) -> List[Dict[str, Any]]:
        sections = []
        content = profile.get("content", {}).get("sections", [])
        
        for i, section in enumerate(content[:5]):  # Limit to first 5 sections
            sections.append({
                "order": i,
                "type": section.get("type", "content"),
                "layout_treatment": self._get_section_treatment(pattern, section.get("type")),
            })
        
        return sections
    
    def _get_section_treatment(self, pattern: str, section_type: str) -> str:
        treatments = {
            "hero": f"{pattern} hero treatment",
            "features": f"{pattern} feature grid",
            "testimonial": f"{pattern} testimonial display",
            "cta": f"{pattern} call-to-action block",
            "content": f"{pattern} content area",
        }
        return treatments.get(section_type, f"{pattern} standard section")


class VisualStrategyEngine:
    """Generates visual strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> VisualStrategy:
        visual = profile.get("visual", {})
        
        density = visual.get("density", "medium")
        contrast = visual.get("contrast", "medium")
        
        recommendations = []
        
        if density == "high":
            recommendations.append("Reduce element count per section by 20-30%")
            recommendations.append("Increase padding between major sections")
        
        if contrast == "low":
            recommendations.append("Increase contrast between primary and secondary elements")
            recommendations.append("Use color or size to establish clearer hierarchy")
        
        if not recommendations:
            recommendations.append("Maintain current visual balance while refining details")
        
        return VisualStrategy(
            density=density,
            negative_space="generous" if density == "low" else "balanced",
            contrast_level=contrast,
            depth=visual.get("depth", "subtle"),
            hierarchy="clear" if visual.get("hierarchy") else "needs_improvement",
            rhythm="consistent",
            composition_notes="Focus on creating visual flow between sections",
            recommendations=recommendations,
        )


class TypographyStrategyEngine:
    """Generates typography strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> TypographyStrategy:
        typography = profile.get("typography", {})
        
        hierarchy = typography.get("hierarchy", {})
        if not hierarchy:
            hierarchy = {
                "H1": "Display - Primary headline",
                "H2": "Section headers",
                "H3": "Subsection headers",
                "body": "Body text",
            }
        
        recommendations = []
        
        if not typography.get("font_pairing"):
            recommendations.append("Consider a complementary font pairing for variety")
        
        if not typography.get("line_height"):
            recommendations.append("Set line-height to 1.5-1.6 for body text readability")
        
        if not typography.get("max_width"):
            recommendations.append("Limit line length to 60-75 characters for optimal reading")
        
        return TypographyStrategy(
            hierarchy=hierarchy,
            primary_font=typography.get("primary_font"),
            secondary_font=typography.get("secondary_font"),
            sizes=typography.get("sizes", {}),
            weights=typography.get("weights", {}),
            line_length=typography.get("line_length", "65ch"),
            line_height=typography.get("line_height", "1.6"),
            letter_spacing=typography.get("letter_spacing", "normal"),
            recommendations=recommendations,
        )


class ColorStrategyEngine:
    """Generates color strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> ColorStrategy:
        colors = profile.get("colors", {})
        brand = profile.get("brand", {})
        
        # Preserve brand colors
        primary = colors.get("primary") or brand.get("primary_color")
        secondary = colors.get("secondary") or brand.get("secondary_color")
        
        recommendations = []
        
        if not colors.get("accent"):
            recommendations.append("Add an accent color for CTAs and interactive elements")
        
        if not colors.get("semantic"):
            recommendations.append("Define semantic colors for success, warning, error states")
        
        brand_notes = ""
        if primary:
            brand_notes = f"Preserving primary brand color ({primary}) for consistency"
        
        return ColorStrategy(
            primary=primary,
            secondary=secondary,
            accent=colors.get("accent"),
            background=colors.get("background", "#ffffff"),
            foreground=colors.get("foreground", "#000000"),
            muted=colors.get("muted"),
            semantic=colors.get("semantic", {}),
            brand_preservation_notes=brand_notes,
            recommendations=recommendations,
        )


class ComponentStrategyEngine:
    """Generates component strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> ComponentStrategy:
        components = profile.get("components", [])
        
        preserve = []
        remove = []
        modify = []
        create = []
        
        # Analyze existing components
        for comp in components:
            comp_name = comp.get("name", "unknown")
            status = comp.get("status", "keep")
            
            if status == "good" or comp.get("accessible", False):
                preserve.append(comp_name)
            elif status == "poor":
                remove.append(comp_name)
            elif status == "needs_work":
                modify.append({"component": comp_name, "reason": comp.get("issues", "Needs refinement")})
        
        # Recommend libraries based on needs
        recommended_libs = []
        if any(c.get("type") == "form" for c in components):
            recommended_libs.append("Radix UI")
        if any(c.get("type") == "button" for c in components):
            recommended_libs.append("shadcn/ui")
        if any(c.get("type") == "icon" for c in components):
            recommended_libs.append("Lucide")
        
        # Ensure we have some defaults
        if not preserve:
            preserve.append("navigation")
            preserve.append("footer")
        
        return ComponentStrategy(
            preserve=preserve,
            remove=remove,
            modify=modify,
            replace=[],
            create=create,
            recommended_libraries=recommended_libs if recommended_libs else ["shadcn/ui", "Lucide"],
            minimum_stack_principle=True,
        )


class MotionStrategyEngine:
    """Generates motion/animation strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> MotionStrategy:
        motion = profile.get("motion", {})
        accessibility = profile.get("accessibility", {})
        
        intensity = motion.get("intensity", "medium")
        use_animation = intensity != "none"
        
        where_to_use = []
        where_to_avoid = []
        accessibility_considerations = []
        
        if use_animation:
            where_to_use = [
                "Micro-interactions on buttons and links",
                "Page transitions for smooth navigation",
                "Loading states for async operations",
            ]
            where_to_avoid = [
                "Auto-playing video or audio",
                "Continuous looping animations",
                "Flash effects that could trigger seizures",
            ]
        
        if accessibility.get("reduce_motion_preference", False):
            accessibility_considerations.append(
                "Respect prefers-reduced-motion media query"
            )
            accessibility_considerations.append(
                "Provide non-animated alternatives for all motion"
            )
        
        return MotionStrategy(
            use_animation=use_animation,
            intensity=intensity,
            duration_range="200ms-500ms for micro-interactions",
            where_to_use=where_to_use,
            where_to_avoid=where_to_avoid,
            accessibility_considerations=accessibility_considerations,
            performance_impact="low" if intensity in ["none", "low"] else "medium",
            recommendations=[
                "Use CSS transforms for performant animations",
                "Avoid animating layout properties like width/height",
            ] if use_animation else ["Consider static design for maximum performance"],
        )


class ContentHierarchyEngine:
    """Generates content hierarchy strategy"""
    
    def analyze(self, profile: Dict[str, Any]) -> ContentHierarchyStrategy:
        content = profile.get("content", {})
        sections = content.get("sections", [])
        
        primary = []
        secondary = []
        tertiary = []
        
        for section in sections:
            priority = section.get("priority", "secondary")
            section_type = section.get("type", "content")
            
            if priority == "high" or section_type in ["hero", "value_prop"]:
                primary.append(section.get("title", section_type))
            elif priority == "medium" or section_type in ["features", "benefits"]:
                secondary.append(section.get("title", section_type))
            else:
                tertiary.append(section.get("title", section_type))
        
        fold_priority = primary[:2] if primary else ["hero"]
        
        return ContentHierarchyStrategy(
            primary_content=primary,
            secondary_content=secondary,
            tertiary_content=tertiary,
            fold_priority=fold_priority,
            recommendations=[
                "Place most important content above the fold",
                "Use visual hierarchy to guide attention to primary content",
            ],
        )


class PerformanceStrategyEngine:
    """Generates performance optimization strategy"""
    
    def analyze(self, profile: Dict[str, Any]) -> PerformanceStrategy:
        performance = profile.get("performance", {})
        
        image_opts = []
        js_opts = []
        font_opts = []
        
        if performance.get("large_images", False):
            image_opts.append("Compress images using modern formats (WebP, AVIF)")
            image_opts.append("Implement responsive images with srcset")
        
        if performance.get("heavy_js", False):
            js_opts.append("Code-split JavaScript bundles")
            js_opts.append("Defer non-critical JavaScript")
        
        if performance.get("many_fonts", False):
            font_opts.append("Limit to 2-3 font families")
            font_opts.append("Use font-display: swap for faster rendering")
        
        return PerformanceStrategy(
            image_optimization=image_opts if image_opts else ["Use appropriate image formats"],
            js_optimization=js_opts if js_opts else ["Minimize JavaScript bundle size"],
            font_optimization=font_opts if font_opts else ["Optimize font loading"],
            animation_optimization=["Use CSS transforms instead of layout animations"],
            dependency_optimization=["Audit and remove unused dependencies"],
            lazy_loading=["images", "below-fold-content"],
            caching_strategy=["Implement service worker for static assets"],
            recommendations=[
                "Target Core Web Vitals scores in green range",
                "Implement performance monitoring",
            ],
        )


class AccessibilityStrategyEngine:
    """Generates accessibility strategy"""
    
    def analyze(self, profile: Dict[str, Any]) -> AccessibilityStrategy:
        accessibility = profile.get("accessibility", {})
        
        contrast_issues = []
        focus_management = []
        keyboard_nav = []
        recommendations = []
        
        contrast_ratio = accessibility.get("contrast_ratio", 4.5)
        if contrast_ratio < 4.5:
            contrast_issues.append({
                "issue": "Insufficient color contrast",
                "current": contrast_ratio,
                "required": 4.5,
            })
            recommendations.append("Adjust colors to meet WCAG AA contrast requirements")
        
        if not accessibility.get("keyboard_accessible", True):
            keyboard_nav.append("Ensure all interactive elements are keyboard accessible")
            recommendations.append("Test navigation using only keyboard")
        
        if not accessibility.get("focus_visible", True):
            focus_management.append("Add visible focus indicators for all interactive elements")
            recommendations.append("Implement custom focus styles matching brand")
        
        recommendations.append("Conduct accessibility audit with automated tools")
        recommendations.append("Test with screen readers (NVDA, VoiceOver)")
        
        return AccessibilityStrategy(
            contrast_issues=contrast_issues,
            focus_management=focus_management if focus_management else ["Maintain visible focus states"],
            keyboard_navigation=keyboard_nav if keyboard_nav else ["Ensure full keyboard support"],
            semantic_html=["Use appropriate HTML5 semantic elements"],
            aria_recommendations=["Add ARIA labels where native semantics are insufficient"],
            motion_sensitivity=["Respect prefers-reduced-motion"],
            touch_targets=["Ensure minimum 44x44px touch targets"],
            wcag_level="AA",
            recommendations=recommendations,
        )


class RiskEngine:
    """Identifies design risks"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[DesignRisk]:
        risks = []
        
        # Check for radical redesign risk
        if profile.get("redesign_scope") == "complete":
            risks.append(DesignRisk(
                risk="Complete redesign may alienate existing users",
                severity="medium",
                likelihood="medium",
                impact="User confusion and potential churn",
                mitigation="Conduct user testing and consider phased rollout",
            ))
        
        # Check for performance risk
        visual = profile.get("visual", {})
        if visual.get("complexity") == "high":
            risks.append(DesignRisk(
                risk="Complex visual design may impact performance",
                severity="medium",
                likelihood="high",
                impact="Slow page loads and poor Core Web Vitals",
                mitigation="Optimize assets and implement lazy loading",
            ))
        
        # Check for accessibility risk
        accessibility = profile.get("accessibility", {})
        if accessibility.get("compliance_level", "AA") == "none":
            risks.append(DesignRisk(
                risk="Non-compliant design may face legal challenges",
                severity="high",
                likelihood="low",
                impact="Legal liability and excluded users",
                mitigation="Prioritize WCAG AA compliance from start",
            ))
        
        # Default risk
        if not risks:
            risks.append(DesignRisk(
                risk="Design changes may not achieve desired conversion lift",
                severity="low",
                likelihood="medium",
                impact="ROI below expectations",
                mitigation="Implement A/B testing to validate changes",
            ))
        
        return risks


class RedesignIntelligenceEngine:
    """Main engine that coordinates all analysis components"""
    
    def __init__(self):
        self.preserve_engine = PreserveEngine()
        self.remove_engine = RemoveEngine()
        self.improvement_engine = ImprovementEngine()
        self.layout_engine = LayoutStrategyEngine()
        self.visual_engine = VisualStrategyEngine()
        self.typography_engine = TypographyStrategyEngine()
        self.color_engine = ColorStrategyEngine()
        self.component_engine = ComponentStrategyEngine()
        self.motion_engine = MotionStrategyEngine()
        self.content_hierarchy_engine = ContentHierarchyEngine()
        self.performance_engine = PerformanceStrategyEngine()
        self.accessibility_engine = AccessibilityStrategyEngine()
        self.risk_engine = RiskEngine()
    
    def analyze(self, profile: Dict[str, Any]) -> RedesignStrategy:
        """Analyze a WebsiteDesignProfile and produce a RedesignStrategy"""
        
        # Handle empty or minimal profiles
        if not profile:
            profile = {"content": {"sections": []}}
        
        # Run all engines
        preserve_decisions = self.preserve_engine.analyze(profile)
        remove_decisions = self.remove_engine.analyze(profile)
        improve_decisions = self.improvement_engine.analyze(profile)
        layout_strategy = self.layout_engine.analyze(profile)
        visual_strategy = self.visual_engine.analyze(profile)
        typography_strategy = self.typography_engine.analyze(profile)
        color_strategy = self.color_engine.analyze(profile)
        component_strategy = self.component_engine.analyze(profile)
        motion_strategy = self.motion_engine.analyze(profile)
        content_hierarchy = self.content_hierarchy_engine.analyze(profile)
        performance_strategy = self.performance_engine.analyze(profile)
        accessibility_strategy = self.accessibility_engine.analyze(profile)
        risks = self.risk_engine.analyze(profile)
        
        # Generate project summary
        brand_name = profile.get("brand", {}).get("name", "Unknown Project")
        industry = profile.get("industry", "General")
        project_summary = f"Redesign strategy for {brand_name} in the {industry} sector"
        
        # Generate original analysis
        original_analysis = self._generate_original_analysis(profile)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            preserve_decisions,
            remove_decisions,
            improve_decisions,
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            profile,
            layout_strategy,
            visual_strategy,
        )
        
        # Get recommended patterns and resources
        recommended_patterns = [layout_strategy.pattern]
        recommended_resources = component_strategy.recommended_libraries
        
        return RedesignStrategy(
            project_summary=project_summary,
            original_analysis=original_analysis,
            preserve=preserve_decisions,
            remove=remove_decisions,
            improve=improve_decisions,
            restructure=self._generate_restructure_recommendations(profile),
            visual_strategy=visual_strategy,
            layout_strategy=layout_strategy,
            typography_strategy=typography_strategy,
            color_strategy=color_strategy,
            component_strategy=component_strategy,
            motion_strategy=motion_strategy,
            content_hierarchy=content_hierarchy,
            performance_strategy=performance_strategy,
            accessibility_strategy=accessibility_strategy,
            risks=risks,
            recommended_patterns=recommended_patterns,
            recommended_resources=recommended_resources,
            confidence=confidence,
            reasoning=reasoning,
        )
    
    def _generate_original_analysis(self, profile: Dict[str, Any]) -> str:
        """Generate analysis of the original design"""
        parts = []
        
        brand = profile.get("brand", {})
        if brand.get("name"):
            parts.append(f"Brand: {brand.get('name')}")
        
        industry = profile.get("industry")
        if industry:
            parts.append(f"Industry: {industry}")
        
        visual = profile.get("visual", {})
        if visual:
            parts.append(f"Visual style: {visual.get('style', 'contemporary')}")
        
        content = profile.get("content", {})
        section_count = len(content.get("sections", []))
        parts.append(f"Content sections: {section_count}")
        
        return "; ".join(parts) if parts else "Standard website design requiring strategic redesign"
    
    def _calculate_confidence(
        self,
        preserve: List[PreserveDecision],
        remove: List[RemoveDecision],
        improve: List[ImproveDecision],
    ) -> float:
        """Calculate overall confidence score"""
        all_decisions = preserve + remove + improve
        if not all_decisions:
            return 0.5
        
        total_confidence = sum(d.confidence for d in all_decisions)
        return round(total_confidence / len(all_decisions), 2)
    
    def _generate_reasoning(
        self,
        profile: Dict[str, Any],
        layout: LayoutStrategy,
        visual: VisualStrategy,
    ) -> str:
        """Generate reasoning for the strategy"""
        industry = profile.get("industry", "general")
        brand = profile.get("brand", {})
        personality = brand.get("personality", "modern")
        
        return (
            f"Strategy tailored for {industry} industry with {personality} brand personality. "
            f"Layout pattern '{layout.pattern}' selected to balance industry conventions with brand differentiation. "
            f"Visual approach emphasizes {visual.density} density with {visual.contrast_level} contrast."
        )
    
    def _generate_restructure_recommendations(
        self,
        profile: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate restructuring recommendations"""
        recommendations = []
        
        content = profile.get("content", {})
        sections = content.get("sections", [])
        
        if len(sections) > 6:
            recommendations.append({
                "action": "consolidate",
                "target": "content_sections",
                "reason": "Reduce from {} to 5-6 focused sections".format(len(sections)),
            })
        
        navigation = profile.get("navigation", {})
        nav_items = navigation.get("items", [])
        if len(nav_items) > 7:
            recommendations.append({
                "action": "simplify",
                "target": "navigation",
                "reason": "Reduce navigation items for clearer information architecture",
            })
        
        if not recommendations:
            recommendations.append({
                "action": "maintain",
                "target": "overall_structure",
                "reason": "Current structure is sound; focus on visual refinement",
            })
        
        return recommendations


def run_redesign_intelligence(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the redesign intelligence skill"""
    engine = RedesignIntelligenceEngine()
    strategy = engine.analyze(profile)
    return strategy.to_dict()
