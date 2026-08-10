"""
Redesign Intelligence Engine V0.1

Transforms WebsiteDesignProfile into RedesignStrategy
"""
from typing import Dict, Any, Optional, List
import random

from .color_intelligence import PaletteGenerator, normalize_hex
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


class PreserveEngine:
    """Determines what elements should be preserved from the original site"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[PreserveDecision]:
        """Analyze profile and return preservation decisions"""
        decisions = []
        
        if not profile:
            return decisions
        
        # Brand identity preservation
        brand = profile.get("brand", {})
        if brand:
            if brand.get("logo"):
                decisions.append(PreserveDecision(
                    element="logo",
                    reason="Core brand identifier that maintains brand recognition",
                    confidence=0.95
                ))
            
            if brand.get("colors"):
                decisions.append(PreserveDecision(
                    element="brand colors",
                    reason="Primary brand colors establish visual identity",
                    confidence=0.9
                ))
            
            if brand.get("value_proposition"):
                decisions.append(PreserveDecision(
                    element="value proposition",
                    reason="Core messaging that communicates unique value",
                    confidence=0.85
                ))
        
        # SEO structure preservation
        seo = profile.get("seo", {})
        if seo:
            if seo.get("structure"):
                decisions.append(PreserveDecision(
                    element="SEO structure",
                    reason="Maintains search engine visibility and rankings",
                    confidence=0.8
                ))
        
        # Navigation preservation
        navigation = profile.get("navigation", {})
        if navigation:
            if navigation.get("useful"):
                decisions.append(PreserveDecision(
                    element="effective navigation patterns",
                    reason="Proven navigation that supports user goals",
                    confidence=0.75
                ))
        
        # Accessibility preservation
        accessibility = profile.get("accessibility", {})
        if accessibility:
            if accessibility.get("good_elements"):
                decisions.append(PreserveDecision(
                    element="accessible components",
                    reason="Elements with good accessibility should be maintained",
                    confidence=0.85
                ))
        
        # Content preservation
        content = profile.get("content", {})
        if content:
            if content.get("relevant"):
                decisions.append(PreserveDecision(
                    element="relevant content",
                    reason="Content that serves user needs and business goals",
                    confidence=0.8
                ))
        
        # Functional components
        components = profile.get("components", {})
        if components:
            functional = [c for c in components if c.get("functional", False)]
            if functional:
                decisions.append(PreserveDecision(
                    element="functional components",
                    reason="Components that work well and serve clear purposes",
                    confidence=0.75
                ))
        
        return decisions


class RemoveEngine:
    """Detects elements that should be removed from the original site"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[RemoveDecision]:
        """Analyze profile and return removal decisions"""
        decisions = []
        
        if not profile:
            return decisions
        
        # Check for unnecessary decoration
        visual = profile.get("visual", {})
        if visual:
            if visual.get("excessive_shadows", False):
                decisions.append(RemoveDecision(
                    element="excessive shadows",
                    reason="Shadows that don't add depth or hierarchy reduce clarity",
                    confidence=0.8
                ))
            
            if visual.get("arbitrary_gradients", False):
                decisions.append(RemoveDecision(
                    element="arbitrary gradients",
                    reason="Gradients without purpose create visual noise",
                    confidence=0.75
                ))
            
            if visual.get("high_density", False):
                decisions.append(RemoveDecision(
                    element="unnecessary decorative elements",
                    reason="High visual density reduces readability and focus",
                    confidence=0.7
                ))
        
        # Check for unnecessary animations
        motion = profile.get("motion", {})
        if motion:
            if motion.get("excessive", False):
                decisions.append(RemoveDecision(
                    element="unnecessary animations",
                    reason="Animations without purpose distract and reduce performance",
                    confidence=0.8
                ))
        
        # Check for redundant content
        content = profile.get("content", {})
        if content:
            if content.get("redundant_sections"):
                decisions.append(RemoveDecision(
                    element="redundant content sections",
                    reason="Repeated information creates confusion and wastes space",
                    confidence=0.75
                ))
        
        # Check for repeated components
        components = profile.get("components", {})
        if components:
            repeated = [c for c in components if c.get("repeated", False)]
            if repeated:
                decisions.append(RemoveDecision(
                    element="repeated components",
                    reason="Duplicate components create redundancy",
                    confidence=0.7
                ))
        
        # Check for generic UI patterns
        ui = profile.get("ui", {})
        if ui:
            if ui.get("generic_patterns"):
                decisions.append(RemoveDecision(
                    element="generic UI patterns",
                    reason="Template-like patterns reduce brand differentiation",
                    confidence=0.65
                ))
        
        # Check for obsolete patterns
        patterns = profile.get("patterns", {})
        if patterns:
            if patterns.get("obsolete"):
                decisions.append(RemoveDecision(
                    element="obsolete visual patterns",
                    reason="Outdated design patterns reduce perceived quality",
                    confidence=0.7
                ))
        
        return decisions


class ImprovementEngine:
    """Detects opportunities for improvement"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[ImproveDecision]:
        """Analyze profile and return improvement decisions"""
        improvements = []
        
        if not profile:
            return improvements
        
        # Visual improvements
        visual = profile.get("visual", {})
        if visual:
            if visual.get("density") == "high":
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.VISUAL,
                    current_state="High visual density throughout the layout",
                    problem="Too many elements competing for attention reduces focus",
                    proposed_change="Increase negative space, reduce element count per section",
                    expected_benefit="Improved readability and clearer visual hierarchy",
                    priority=Priority.HIGH,
                    confidence=0.85
                ))
            
            if visual.get("contrast") == "low":
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.VISUAL,
                    current_state="Low contrast between text and background",
                    problem="Reduced readability and accessibility issues",
                    proposed_change="Increase contrast ratio to meet WCAG AA standards",
                    expected_benefit="Better readability for all users, improved accessibility",
                    priority=Priority.CRITICAL,
                    confidence=0.9
                ))
        
        # Layout improvements
        layout = profile.get("layout", {})
        if layout:
            if layout.get("pattern") == "predictable":
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.LAYOUT,
                    current_state="Predictable left-text/right-image pattern throughout",
                    problem="Monotonous layout fails to engage users",
                    proposed_change="Introduce asymmetric or editorial layouts for variety",
                    expected_benefit="Increased visual interest and engagement",
                    priority=Priority.MEDIUM,
                    confidence=0.75
                ))
        
        # Typography improvements
        typography = profile.get("typography", {})
        if typography:
            if not typography.get("hierarchy"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.TYPOGRAPHY,
                    current_state="Unclear typographic hierarchy",
                    problem="Users cannot quickly scan and understand content structure",
                    proposed_change="Establish clear H1/H2/H3 hierarchy with distinct sizes and weights",
                    expected_benefit="Improved scannability and content comprehension",
                    priority=Priority.HIGH,
                    confidence=0.85
                ))
        
        # Content improvements
        content = profile.get("content", {})
        if content:
            if content.get("weak_headlines"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.CONTENT,
                    current_state="Generic or weak headlines",
                    problem="Fails to capture attention and communicate value",
                    proposed_change="Rewrite headlines to be specific, benefit-focused, and action-oriented",
                    expected_benefit="Higher engagement and conversion rates",
                    priority=Priority.HIGH,
                    confidence=0.8
                ))
        
        # Conversion improvements
        conversion = profile.get("conversion", {})
        if conversion:
            if conversion.get("weak_cta"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.CONVERSION,
                    current_state="Weak or unclear call-to-action",
                    problem="Users don't know what action to take next",
                    proposed_change="Create prominent, action-oriented CTAs with clear value",
                    expected_benefit="Increased conversion rates and user actions",
                    priority=Priority.CRITICAL,
                    confidence=0.85
                ))
        
        # Accessibility improvements
        accessibility = profile.get("accessibility", {})
        if accessibility:
            if accessibility.get("issues"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.ACCESSIBILITY,
                    current_state="Accessibility barriers detected",
                    problem="Some users cannot effectively use the website",
                    proposed_change="Address contrast, focus management, and keyboard navigation",
                    expected_benefit="Inclusive experience for all users, legal compliance",
                    priority=Priority.CRITICAL,
                    confidence=0.9
                ))
        
        # Performance improvements
        performance = profile.get("performance", {})
        if performance:
            if performance.get("slow_loading"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.PERFORMANCE,
                    current_state="Slow page load times",
                    problem="Users abandon before content loads",
                    proposed_change="Optimize images, reduce JavaScript, implement lazy loading",
                    expected_benefit="Faster load times, better retention and SEO",
                    priority=Priority.HIGH,
                    confidence=0.85
                ))
        
        # Responsive improvements
        responsive = profile.get("responsive", {})
        if responsive:
            if responsive.get("mobile_issues"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.RESPONSIVE,
                    current_state="Poor mobile experience",
                    problem="Mobile users have difficulty navigating and reading content",
                    proposed_change="Implement mobile-first responsive design with appropriate breakpoints",
                    expected_benefit="Better experience for majority of users on mobile devices",
                    priority=Priority.HIGH,
                    confidence=0.85
                ))
        
        # Interaction improvements
        interaction = profile.get("interaction", {})
        if interaction:
            if interaction.get("unclear_feedback"):
                improvements.append(ImproveDecision(
                    category=ImprovementCategory.INTERACTION,
                    current_state="Unclear interactive feedback",
                    problem="Users unsure if actions were successful",
                    proposed_change="Add clear hover, focus, and active states with appropriate feedback",
                    expected_benefit="Increased confidence and reduced user errors",
                    priority=Priority.MEDIUM,
                    confidence=0.75
                ))
        
        return improvements


class LayoutStrategyEngine:
    """Generates layout strategy recommendations"""
    
    def __init__(self):
        self.layout_patterns = list(LayoutPattern)
    
    def analyze(self, profile: Dict[str, Any]) -> LayoutStrategy:
        """Generate layout strategy based on profile"""
        
        # Default pattern selection based on profile characteristics
        industry = profile.get("industry", "general")
        brand_personality = profile.get("brand", {}).get("personality", "neutral")
        content_type = profile.get("content_type", "mixed")
        audience = profile.get("audience", "general")
        
        # Determine recommended pattern based on context
        pattern_scores = {p: 0 for p in self.layout_patterns}
        
        # Industry-based adjustments
        if industry in ["creative", "design", "art"]:
            pattern_scores[LayoutPattern.EXPERIMENTAL] += 3
            pattern_scores[LayoutPattern.ASYMMETRIC] += 2
            pattern_scores[LayoutPattern.IMMERSIVE] += 2
        elif industry in ["corporate", "finance", "legal"]:
            pattern_scores[LayoutPattern.GRID] += 3
            pattern_scores[LayoutPattern.CENTERED] += 2
        elif industry in ["editorial", "publishing", "news"]:
            pattern_scores[LayoutPattern.EDITORIAL] += 3
            pattern_scores[LayoutPattern.STORYTELLING] += 2
        elif industry in ["tech", "startup"]:
            pattern_scores[LayoutPattern.BENTO] += 2
            pattern_scores[LayoutPattern.ASYMMETRIC] += 2
            pattern_scores[LayoutPattern.OVERLAPPING] += 1
        elif industry in ["fashion", "lifestyle"]:
            pattern_scores[LayoutPattern.FULL_BLEED] += 3
            pattern_scores[LayoutPattern.IMMERSIVE] += 2
        elif industry in ["ecommerce", "retail"]:
            pattern_scores[LayoutPattern.GRID] += 2
            pattern_scores[LayoutPattern.BENTO] += 2
        
        # Personality-based adjustments
        if brand_personality in ["bold", "adventurous"]:
            pattern_scores[LayoutPattern.DIAGONAL] += 2
            pattern_scores[LayoutPattern.ASYMMETRIC] += 2
        elif brand_personality in ["elegant", "sophisticated"]:
            pattern_scores[LayoutPattern.EDITORIAL] += 2
            pattern_scores[LayoutPattern.CENTERED] += 1
        elif brand_personality in ["playful", "friendly"]:
            pattern_scores[LayoutPattern.OVERLAPPING] += 2
            pattern_scores[LayoutPattern.LAYERED] += 2
        
        # Content type adjustments
        if content_type == "visual_heavy":
            pattern_scores[LayoutPattern.FULL_BLEED] += 2
            pattern_scores[LayoutPattern.IMMERSIVE] += 2
        elif content_type == "text_heavy":
            pattern_scores[LayoutPattern.EDITORIAL] += 2
            pattern_scores[LayoutPattern.CENTERED] += 1
        elif content_type == "product_focused":
            pattern_scores[LayoutPattern.BENTO] += 2
            pattern_scores[LayoutPattern.GRID] += 2
        
        # Avoid predictable patterns
        pattern_scores[LayoutPattern.SPLIT] -= 1  # Common left/right pattern
        
        # Sort by score
        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: x[1], reverse=True)
        recommended = sorted_patterns[0][0]
        alternatives = [p[0] for p in sorted_patterns[1:4]]
        
        # Generate reasoning
        reasoning = f"Selected {recommended.value} layout based on industry ({industry}), "
        reasoning += f"brand personality ({brand_personality}), and content type ({content_type}). "
        reasoning += "This pattern provides visual interest while supporting content goals."
        
        return LayoutStrategy(
            recommended_pattern=recommended,
            alternative_patterns=alternatives,
            reasoning=reasoning,
            grid_system="12-column flexible grid",
            spacing_scale="8px base unit",
            container_width="1200px max-width",
            breakpoints=["640px", "768px", "1024px", "1280px"]
        )


class VisualStrategyEngine:
    """Generates visual strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> VisualStrategy:
        """Generate visual strategy based on profile"""
        
        visual = profile.get("visual", {})
        brand = profile.get("brand", {})
        
        # Analyze current state
        current_density = visual.get("density", "medium")
        current_contrast = visual.get("contrast", "medium")
        
        recommendations = []
        
        # Density recommendations
        if current_density == "high":
            recommendations.append(
                "Reduce visual density by increasing whitespace between sections"
            )
            recommendations.append(
                "Group related elements more tightly while increasing space between groups"
            )
        elif current_density == "low":
            recommendations.append(
                "Consider adding subtle visual elements to fill excessive whitespace"
            )
        
        # Contrast recommendations
        if current_contrast == "low":
            recommendations.append(
                "Increase contrast between primary content and background"
            )
            recommendations.append(
                "Ensure text meets WCAG AA contrast requirements (4.5:1 for normal text)"
            )
        
        # Hierarchy recommendations
        if not visual.get("clear_hierarchy", True):
            recommendations.append(
                "Establish clearer visual hierarchy through size, weight, and color variations"
            )
        
        # Composition recommendations
        composition = visual.get("composition", "")
        if composition == "centered_heavy":
            recommendations.append(
                "Introduce asymmetric compositions to create visual tension and interest"
            )
        
        return VisualStrategy(
            density="medium",
            negative_space="generous",
            contrast_level="high",
            depth="subtle",
            hierarchy="clear",
            rhythm="consistent",
            repetition="purposeful",
            composition="balanced",
            scale_relationships="varied",
            image_text_ratio="60/40",
            recommendations=recommendations
        )


class TypographyStrategyEngine:
    """Generates typography strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> TypographyStrategy:
        """Generate typography strategy based on profile"""
        
        typography = profile.get("typography", {})
        brand = profile.get("brand", {})
        
        hierarchy = {}
        font_sizes = {}
        font_weights = {}
        recommendations = []
        
        # Establish hierarchy
        hierarchy["H1"] = "Primary headline - main page title"
        hierarchy["H2"] = "Section headlines"
        hierarchy["H3"] = "Subsection headlines"
        hierarchy["body"] = "Body text and paragraphs"
        hierarchy["caption"] = "Small supporting text"
        
        # Font size recommendations
        font_sizes["H1"] = "clamp(2.5rem, 5vw, 4rem)"
        font_sizes["H2"] = "clamp(1.75rem, 3vw, 2.5rem)"
        font_sizes["H3"] = "clamp(1.25rem, 2vw, 1.75rem)"
        font_sizes["body"] = "1rem (16px)"
        font_sizes["caption"] = "0.875rem (14px)"
        
        # Font weight recommendations
        font_weights["H1"] = "700 (bold)"
        font_weights["H2"] = "600 (semi-bold)"
        font_weights["H3"] = "600 (semi-bold)"
        font_weights["body"] = "400 (regular)"
        font_weights["caption"] = "400 (regular)"
        
        # Check existing typography
        existing_fonts = typography.get("fonts", [])
        if existing_fonts:
            recommendations.append(
                f"Evaluate existing fonts ({', '.join(existing_fonts)}) for adequacy before introducing new typefaces"
            )
        else:
            recommendations.append(
                "Select a primary font family that reflects brand personality"
            )
            recommendations.append(
                "Consider a complementary secondary font for headings or accents"
            )
        
        # Line length recommendation
        recommendations.append(
            "Maintain optimal line length of 45-75 characters for body text"
        )
        
        return TypographyStrategy(
            hierarchy=hierarchy,
            font_sizes=font_sizes,
            font_weights=font_weights,
            line_length="65 characters average",
            line_height="1.5 for body, 1.2 for headings",
            letter_spacing="-0.02em for headings, 0 for body",
            font_combinations=[],
            recommendations=recommendations
        )


class ColorStrategyEngine:
    """Generates color strategy recommendations.

    When the profile already has a full, deliberate palette, this is
    preserved as-is (brand preservation always wins — see
    ARCHITECTURE_PRINCIPLES.md §12). When secondary/accent/semantic
    colors are missing, they are no longer left as a text suggestion
    ("define a color that reflects brand identity") — they're generated
    from the real brand primary color using PaletteGenerator, which
    applies actual color theory (harmony rules, WCAG-verified contrast,
    a brand-anchored tint/shade ramp). See color_intelligence.py.
    """

    def __init__(self, palette_generator: Optional[PaletteGenerator] = None):
        self.palette_generator = palette_generator or PaletteGenerator()

    def analyze(self, profile: Dict[str, Any]) -> ColorStrategy:
        """Generate color strategy based on profile"""
        
        brand = profile.get("brand", {})
        existing_colors = profile.get("colors", {})
        
        recommendations = []
        
        # Brand preservation check
        preserve_brand = brand.get("preserve_colors", True)
        
        primary = existing_colors.get("primary")
        secondary = existing_colors.get("secondary")
        accent = existing_colors.get("accent")
        background = existing_colors.get("background")
        foreground = existing_colors.get("foreground")
        muted = existing_colors.get("muted")
        semantic = existing_colors.get("semantic", {})
        primary_ramp: Dict[str, str] = {}

        has_full_palette = all([secondary, accent, background, foreground, muted, semantic])

        if primary and not has_full_palette:
            # This is the real work: build a complete, accessible palette
            # outward from the one color we know is genuinely the
            # client's brand — instead of leaving gaps or generic hex
            # defaults for a human to fill in later.
            try:
                normalized_primary = normalize_hex(primary)
                generated = self.palette_generator.generate(normalized_primary)

                secondary = secondary or generated.secondary
                accent = accent or generated.accent
                background = background or generated.background
                foreground = foreground or generated.foreground
                muted = muted or generated.muted
                semantic = semantic or generated.semantic_colors
                primary_ramp = generated.primary_ramp

                recommendations.append(
                    f"Generated an extended palette from the brand primary "
                    f"color ({normalized_primary}) using {generated.harmony_used} "
                    f"harmony — kept the brand color exactly as-is and built "
                    f"secondary/accent/neutrals around it."
                )
                recommendations.extend(generated.notes)
                accessibility_pct = generated.accessibility_score()
                recommendations.append(
                    f"Generated palette accessibility: {accessibility_pct:.0f}% "
                    f"of checked color pairs meet WCAG AA contrast."
                )
            except ValueError:
                recommendations.append(
                    f"Primary color '{primary}' is not a valid hex color — "
                    f"could not generate an extended palette from it."
                )
        elif primary:
            recommendations.append(f"Maintain primary brand color ({primary}) for consistency")
        else:
            recommendations.append(
                "No brand primary color was found in the profile — Brand DNA "
                "Extractor must supply one before a real palette can be "
                "generated (see ROADMAP.md FASE 2B)."
            )
        
        if not semantic:
            recommendations.append("Establish semantic colors for success, warning, error, and info states")
        
        return ColorStrategy(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background or "#FFFFFF",
            foreground=foreground or "#1A1A1A",
            muted=muted or "#6B7280",
            primary_ramp=primary_ramp,
            semantic_colors=semantic,
            brand_preservation=preserve_brand,
            recommendations=recommendations
        )


class ComponentStrategyEngine:
    """Generates component strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> ComponentStrategy:
        """Generate component strategy based on profile"""
        
        components = profile.get("components", [])
        recommendations = []
        component_decisions = []
        
        # Analyze existing components
        seen_components = set()
        for comp in components:
            name = comp.get("name", "unknown")
            if name in seen_components:
                continue
            seen_components.add(name)
            
            action = ComponentAction.PRESERVE
            reason = "Component serves a clear purpose and functions well"
            source = None
            
            # Check for problems
            if comp.get("redundant", False):
                action = ComponentAction.REMOVE
                reason = "Component is redundant with other elements"
            elif comp.get("outdated", False):
                action = ComponentAction.REPLACE
                reason = "Component uses outdated patterns"
                source = "shadcn"
            elif comp.get("needs_modification", False):
                action = ComponentAction.MODIFY
                reason = "Component needs updates for consistency"
            
            component_decisions.append(ComponentRecommendation(
                component_name=name,
                action=action,
                reason=reason,
                source=source,
                alternatives=[]
            ))
        
        # Add missing essential components
        essential_components = {
            "Navigation": ComponentAction.CREATE,
            "Hero": ComponentAction.CREATE,
            "CTA": ComponentAction.CREATE,
            "Footer": ComponentAction.CREATE,
        }
        
        for comp_name, action in essential_components.items():
            if comp_name not in seen_components:
                component_decisions.append(ComponentRecommendation(
                    component_name=comp_name,
                    action=action,
                    reason="Essential component for complete page structure",
                    source="shadcn" if action == ComponentAction.CREATE else None,
                    alternatives=[]
                ))
        
        recommendations.append("Follow minimum sufficient stack principle - only add dependencies when necessary")
        recommendations.append("Prefer accessible, well-tested component libraries")
        recommendations.append("Consider shadcn/ui, Radix UI, React Bits, MagicUI for components")
        
        return ComponentStrategy(
            components=component_decisions,
            minimum_stack_principle=True,
            recommendations=recommendations
        )


class MotionStrategyEngine:
    """Generates motion strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> MotionStrategy:
        """Generate motion strategy based on profile"""
        
        motion = profile.get("motion", {})
        brand = profile.get("brand", {})
        
        # Determine intensity based on brand
        personality = brand.get("personality", "neutral")
        if personality in ["bold", "energetic", "playful"]:
            intensity = "moderate"
        elif personality in ["elegant", "sophisticated", "minimal"]:
            intensity = "subtle"
        else:
            intensity = "subtle"
        
        animated_elements = []
        static_elements = []
        recommendations = []
        
        # Elements that benefit from animation
        animated_elements.extend([
            "Page transitions",
            "Hover states on interactive elements",
            "Loading indicators",
            "Focus indicators",
            "Scroll-triggered reveals (sparingly)"
        ])
        
        # Elements that should remain static
        static_elements.extend([
            "Body text",
            "Static images",
            "Background elements",
            "Form labels"
        ])
        
        # Recommendations
        recommendations.append("Use animation purposefully - every animation should have a reason")
        recommendations.append("Keep animation durations between 150ms-400ms for most interactions")
        recommendations.append("Respect prefers-reduced-motion media query for accessibility")
        recommendations.append("Prioritize performance - avoid animating expensive properties")
        
        # Check for existing motion issues
        if motion.get("excessive", False):
            recommendations.append("Reduce overall animation count to improve performance and clarity")
        
        return MotionStrategy(
            use_animation=True,
            intensity=intensity,
            duration_range="150ms-400ms",
            animated_elements=animated_elements,
            static_elements=static_elements,
            performance_priority=True,
            accessibility_considerations=[
                "Respect prefers-reduced-motion",
                "Provide non-animated alternatives",
                "Avoid auto-playing animations"
            ],
            recommendations=recommendations
        )


class ContentHierarchyEngine:
    """Generates content hierarchy strategy"""
    
    def analyze(self, profile: Dict[str, Any]) -> ContentHierarchyStrategy:
        """Generate content hierarchy strategy based on profile"""
        
        content = profile.get("content", {})
        goals = profile.get("goals", [])
        
        primary_content = []
        secondary_content = []
        tertiary_content = []
        recommendations = []
        
        # Identify primary content based on goals
        if "conversion" in goals:
            primary_content.append("Value proposition")
            primary_content.append("Primary CTA")
        elif "information" in goals:
            primary_content.append("Key information")
            primary_content.append("Navigation")
        elif "engagement" in goals:
            primary_content.append("Engaging visuals")
            primary_content.append("Interactive elements")
        
        # Default primary content
        if not primary_content:
            primary_content.extend([
                "Headline / Value proposition",
                "Primary call-to-action",
                "Key visual or hero element"
            ])
        
        # Secondary content
        secondary_content.extend([
            "Supporting benefits",
            "Social proof (testimonials, logos)",
            "Feature highlights"
        ])
        
        # Tertiary content
        tertiary_content.extend([
            "Detailed specifications",
            "FAQ section",
            "Secondary links",
            "Legal information"
        ])
        
        # Content flow
        content_flow = [
            "Attention-grabbing hero",
            "Value proposition",
            "Supporting evidence",
            "Social proof",
            "Call-to-action",
            "Additional information",
            "Final CTA"
        ]
        
        recommendations.append("Place most important content above the fold")
        recommendations.append("Use progressive disclosure for complex information")
        recommendations.append("Group related content together")
        recommendations.append("Create clear visual separation between content sections")
        
        return ContentHierarchyStrategy(
            primary_content=primary_content,
            secondary_content=secondary_content,
            tertiary_content=tertiary_content,
            content_flow=content_flow,
            fold_strategy="Critical content and primary CTA visible without scrolling",
            recommendations=recommendations
        )


class PerformanceStrategyEngine:
    """Generates performance strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> PerformanceStrategy:
        """Generate performance strategy based on profile"""
        
        performance = profile.get("performance", {})
        recommendations = []
        
        image_optimization = []
        js_optimization = []
        animation_optimization = []
        dependency_optimization = []
        font_optimization = []
        lazy_loading = []
        
        # Image optimization
        image_optimization.append("Use modern formats (WebP, AVIF)")
        image_optimization.append("Implement responsive images with srcset")
        image_optimization.append("Compress images appropriately")
        
        # JS optimization
        js_optimization.append("Minimize JavaScript bundle size")
        js_optimization.append("Code-split where appropriate")
        js_optimization.append("Defer non-critical JavaScript")
        
        # Animation optimization
        animation_optimization.append("Use CSS transforms for animations (GPU-accelerated)")
        animation_optimization.append("Avoid animating layout properties")
        
        # Dependency optimization
        dependency_optimization.append("Audit and remove unused dependencies")
        dependency_optimization.append("Tree-shake where possible")
        
        # Font optimization
        font_optimization.append("Use font-display: swap")
        font_optimization.append("Subset fonts to include only needed characters")
        font_optimization.append("Limit number of font weights and variants")
        
        # Lazy loading
        lazy_loading.append("Images below the fold")
        lazy_loading.append("Non-critical components")
        
        # Additional recommendations based on profile
        if performance.get("slow_images", False):
            recommendations.append("Prioritize image optimization - largest performance gain opportunity")
        
        if performance.get("heavy_js", False):
            recommendations.append("Reduce JavaScript payload - consider lighter alternatives")
        
        if performance.get("too_many_animations", False):
            recommendations.append("Reduce animation complexity for better performance")
        
        recommendations.append("Implement performance budget monitoring")
        recommendations.append("Use Core Web Vitals as performance targets")
        
        return PerformanceStrategy(
            image_optimization=image_optimization,
            js_optimization=js_optimization,
            animation_optimization=animation_optimization,
            dependency_optimization=dependency_optimization,
            font_optimization=font_optimization,
            lazy_loading=lazy_loading,
            recommendations=recommendations
        )


class AccessibilityStrategyEngine:
    """Generates accessibility strategy recommendations"""
    
    def analyze(self, profile: Dict[str, Any]) -> AccessibilityStrategy:
        """Generate accessibility strategy based on profile"""
        
        accessibility = profile.get("accessibility", {})
        existing_issues = accessibility.get("issues", [])
        
        contrast_issues = []
        focus_management = []
        keyboard_navigation = []
        semantic_html = []
        aria_requirements = []
        motion_sensitivity = []
        touch_targets = []
        recommendations = []
        
        # Check for contrast issues
        if accessibility.get("low_contrast", False):
            contrast_issues.append({
                "issue": "Low contrast text",
                "location": "Various sections",
                "wcag": "1.4.3"
            })
        
        # Focus management
        focus_management.append("Ensure visible focus indicators on all interactive elements")
        focus_management.append("Implement logical focus order")
        focus_management.append("Manage focus during dynamic content changes")
        
        # Keyboard navigation
        keyboard_navigation.append("All functionality accessible via keyboard")
        keyboard_navigation.append("Skip links for main content areas")
        keyboard_navigation.append("Keyboard-accessible menus and dropdowns")
        
        # Semantic HTML
        semantic_html.append("Use proper heading hierarchy (H1-H6)")
        semantic_html.append("Semantic landmarks (header, nav, main, footer)")
        semantic_html.append("Appropriate ARIA roles where needed")
        
        # ARIA requirements
        aria_requirements.append("Labels for form inputs")
        aria_requirements.append("ARIA live regions for dynamic content")
        aria_requirements.append("Descriptive link text")
        
        # Motion sensitivity
        motion_sensitivity.append("Respect prefers-reduced-motion media query")
        motion_sensitivity.append("Provide pause controls for auto-playing content")
        
        # Touch targets
        touch_targets.append("Minimum 44x44px touch targets")
        touch_targets.append("Adequate spacing between interactive elements")
        
        # General recommendations
        recommendations.append("Conduct accessibility audit using automated tools")
        recommendations.append("Test with screen readers (NVDA, VoiceOver)")
        recommendations.append("Include users with disabilities in testing")
        recommendations.append("Target WCAG 2.1 AA compliance as minimum")
        
        return AccessibilityStrategy(
            contrast_issues=contrast_issues,
            focus_management=focus_management,
            keyboard_navigation=keyboard_navigation,
            semantic_html=semantic_html,
            aria_requirements=aria_requirements,
            motion_sensitivity=motion_sensitivity,
            touch_targets=touch_targets,
            recommendations=recommendations
        )


class RiskEngine:
    """Identifies potential design risks"""
    
    def analyze(self, profile: Dict[str, Any]) -> List[DesignRisk]:
        """Analyze profile and identify risks"""
        
        risks = []
        
        # Risk: Over-designing
        if profile.get("complexity_preference") == "high":
            risks.append(DesignRisk(
                risk="Over-complicating the design with unnecessary elements",
                severity="medium",
                likelihood="medium",
                impact="Reduced usability and performance",
                mitigation="Apply restraint and prioritize essential elements",
                confidence=0.7
            ))
        
        # Risk: Brand dilution
        brand = profile.get("brand", {})
        if brand.get("strong_identity", False):
            risks.append(DesignRisk(
                risk="Redesign may dilute established brand identity",
                severity="high",
                likelihood="low",
                impact="Loss of brand recognition",
                mitigation="Preserve core brand elements while modernizing execution",
                confidence=0.75
            ))
        
        # Risk: Performance degradation
        if profile.get("motion_preference") == "high":
            risks.append(DesignRisk(
                risk="Excessive animations impacting performance",
                severity="medium",
                likelihood="medium",
                impact="Slow page loads and poor user experience",
                mitigation="Implement performance budgets and optimize animations",
                confidence=0.7
            ))
        
        # Risk: Accessibility gaps
        if not profile.get("accessibility", {}).get("priority", False):
            risks.append(DesignRisk(
                risk="Accessibility may be overlooked in favor of aesthetics",
                severity="high",
                likelihood="medium",
                impact="Excluded users and potential legal issues",
                mitigation="Make accessibility a core requirement from the start",
                confidence=0.8
            ))
        
        # Risk: Content mismatch
        content = profile.get("content", {})
        if content.get("insufficient", False):
            risks.append(DesignRisk(
                risk="Insufficient content for planned layout",
                severity="medium",
                likelihood="medium",
                impact="Empty-looking pages or stretched content",
                mitigation="Plan layout around available content or create content plan",
                confidence=0.65
            ))
        
        # Risk: Mobile compromise
        if profile.get("mobile_importance", "medium") == "low":
            risks.append(DesignRisk(
                risk="Mobile experience may be compromised",
                severity="high",
                likelihood="medium",
                impact="Poor experience for majority of users",
                mitigation="Adopt mobile-first approach regardless of stated priorities",
                confidence=0.75
            ))
        
        return risks


class RedesignIntelligenceEngine:
    """Main engine that orchestrates all analysis engines"""
    
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
        self.content_engine = ContentHierarchyEngine()
        self.performance_engine = PerformanceStrategyEngine()
        self.accessibility_engine = AccessibilityStrategyEngine()
        self.risk_engine = RiskEngine()
    
    def analyze(self, profile: Dict[str, Any]) -> RedesignStrategy:
        """
        Transform WebsiteDesignProfile into RedesignStrategy
        
        Args:
            profile: WebsiteDesignProfile as dictionary
            
        Returns:
            RedesignStrategy with comprehensive recommendations
        """
        
        # Handle empty or incomplete profiles
        if not profile:
            return self._create_empty_profile_strategy()

        # Normalize: WebsiteDesignProfile.to_dict() (website_intelligence)
        # sets unavailable nested sections to None explicitly, not
        # absent — e.g. {"typography": None} rather than omitting the
        # key. dict.get(key, {}) only falls back to {} when the key is
        # MISSING, not when it's present with value None, so every
        # sub-engine below that does profile.get("x", {}).get(...) would
        # crash on a real profile with unavailable sections. This is the
        # integration boundary fix; each sub-engine still uses
        # .get(key, {}) as before.
        profile = {k: (v if v is not None else {}) for k, v in profile.items()}

        # Run all analysis engines
        preserve_decisions = self.preserve_engine.analyze(profile)
        remove_decisions = self.remove_engine.analyze(profile)
        improve_decisions = self.improvement_engine.analyze(profile)
        layout_strategy = self.layout_engine.analyze(profile)
        visual_strategy = self.visual_engine.analyze(profile)
        typography_strategy = self.typography_engine.analyze(profile)
        color_strategy = self.color_engine.analyze(profile)
        component_strategy = self.component_engine.analyze(profile)
        motion_strategy = self.motion_engine.analyze(profile)
        content_hierarchy = self.content_engine.analyze(profile)
        performance_strategy = self.performance_engine.analyze(profile)
        accessibility_strategy = self.accessibility_engine.analyze(profile)
        risks = self.risk_engine.analyze(profile)
        
        # Generate project summary
        project_summary = self._generate_summary(profile)
        
        # Generate original analysis
        original_analysis = self._analyze_original(profile)
        
        # Determine restructure recommendations
        restructure = self._determine_restructure(profile, layout_strategy)
        
        # Get recommended patterns
        recommended_patterns = self._get_recommended_patterns(profile, layout_strategy)
        
        # Get recommended resources
        recommended_resources = self._get_recommended_resources(component_strategy)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            preserve_decisions,
            remove_decisions,
            improve_decisions,
            profile
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            profile,
            preserve_decisions,
            remove_decisions,
            improve_decisions,
            layout_strategy
        )
        
        return RedesignStrategy(
            project_summary=project_summary,
            original_analysis=original_analysis,
            preserve=preserve_decisions,
            remove=remove_decisions,
            improve=improve_decisions,
            restructure=restructure,
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
            reasoning=reasoning
        )
    
    def _create_empty_profile_strategy(self) -> RedesignStrategy:
        """Create a default strategy for empty profiles"""
        return RedesignStrategy(
            project_summary="No profile data provided - generating baseline recommendations",
            original_analysis="Unable to analyze original site due to missing profile data",
            preserve=[],
            remove=[],
            improve=[
                ImproveDecision(
                    category=ImprovementCategory.ACCESSIBILITY,
                    current_state="Unknown - no profile data",
                    problem="Cannot assess accessibility without site analysis",
                    proposed_change="Conduct full accessibility audit",
                    expected_benefit="Ensure inclusive design",
                    priority=Priority.HIGH,
                    confidence=0.5
                )
            ],
            restructure=[],
            visual_strategy=VisualStrategy(recommendations=["Establish visual direction based on brand guidelines"]),
            layout_strategy=LayoutStrategy(
                recommended_pattern=LayoutPattern.CENTERED,
                reasoning="Default centered layout selected due to insufficient profile data"
            ),
            typography_strategy=TypographyStrategy(recommendations=["Define typography system"]),
            color_strategy=ColorStrategy(recommendations=["Define color palette"]),
            component_strategy=ComponentStrategy(recommendations=["Identify required components"]),
            motion_strategy=MotionStrategy(use_animation=False, recommendations=["Define motion guidelines"]),
            content_hierarchy=ContentHierarchyStrategy(recommendations=["Define content strategy"]),
            performance_strategy=PerformanceStrategy(recommendations=["Establish performance budgets"]),
            accessibility_strategy=AccessibilityStrategy(recommendations=["Conduct accessibility audit"]),
            risks=[DesignRisk(
                risk="Insufficient data for informed design decisions",
                severity="high",
                likelihood="high",
                impact="May result in inappropriate design choices",
                mitigation="Gather comprehensive profile data before proceeding",
                confidence=0.95
            )],
            recommended_patterns=["grid", "centered"],
            recommended_resources=[],
            confidence=0.3,
            reasoning="Limited profile data resulted in generic recommendations"
        )
    
    def _generate_summary(self, profile: Dict[str, Any]) -> str:
        """Generate project summary from profile"""
        industry = profile.get("industry", "general")
        brand = profile.get("brand", {})
        goals = profile.get("goals", [])
        
        summary = f"Project in the {industry} sector"
        
        if brand.get("personality"):
            summary += f" with {brand['personality']} brand personality"
        
        if goals:
            summary += f". Primary goals: {', '.join(goals)}"
        
        return summary + "."
    
    def _analyze_original(self, profile: Dict[str, Any]) -> str:
        """Analyze the original site based on profile"""
        analysis_parts = []
        
        visual = profile.get("visual", {})
        if visual:
            if visual.get("density") == "high":
                analysis_parts.append("The current design has high visual density")
            if visual.get("contrast") == "low":
                analysis_parts.append("contrast levels need improvement")
        
        layout = profile.get("layout", {})
        if layout:
            if layout.get("pattern") == "predictable":
                analysis_parts.append("layout follows predictable patterns")
        
        if not analysis_parts:
            return "Original site analysis based on provided profile data."
        
        return ". ".join(analysis_parts) + "."
    
    def _determine_restructure(self, profile: Dict[str, Any], layout_strategy: LayoutStrategy) -> List[str]:
        """Determine restructuring recommendations"""
        restructure = []
        
        # Based on layout change
        if layout_strategy.recommended_pattern != LayoutPattern.GRID:
            restructure.append(
                f"Reorganize content to support {layout_strategy.recommended_pattern.value} layout"
            )
        
        # Based on content hierarchy
        content = profile.get("content", {})
        if content.get("poor_organization", False):
            restructure.append("Reorganize content sections for better flow")
        
        # Based on navigation
        navigation = profile.get("navigation", {})
        if navigation.get("complex", False):
            restructure.append("Simplify navigation structure")
        
        if not restructure:
            restructure.append("Maintain existing structure with refinements")
        
        return restructure
    
    def _get_recommended_patterns(self, profile: Dict[str, Any], layout_strategy: LayoutStrategy) -> List[str]:
        """Get recommended design patterns"""
        patterns = [layout_strategy.recommended_pattern.value]
        patterns.extend([p.value for p in layout_strategy.alternative_patterns[:2]])
        return patterns
    
    def _get_recommended_resources(self, component_strategy: ComponentStrategy) -> List[str]:
        """Get recommended resources"""
        resources = []
        
        # Collect sources from component recommendations
        for comp in component_strategy.components:
            if comp.source and comp.source not in resources:
                resources.append(comp.source)
        
        # Add defaults if empty
        if not resources:
            resources = ["shadcn/ui", "Lucide Icons"]
        
        return resources
    
    def _calculate_confidence(self, preserve: List[PreserveDecision], 
                             remove: List[RemoveDecision],
                             improve: List[ImproveDecision],
                             profile: Dict[str, Any]) -> float:
        """Calculate overall confidence in recommendations"""
        
        if not profile:
            return 0.3
        
        confidences = []
        
        # Average confidence from decisions
        for d in preserve:
            confidences.append(d.confidence)
        for d in remove:
            confidences.append(d.confidence)
        for d in improve:
            confidences.append(d.confidence)
        
        if not confidences:
            return 0.5
        
        avg_confidence = sum(confidences) / len(confidences)
        
        # Adjust based on profile completeness
        profile_completeness = len([v for v in profile.values() if v]) / max(len(profile), 1)
        
        # Weighted average
        return (avg_confidence * 0.7) + (profile_completeness * 0.3)
    
    def _generate_reasoning(self, profile: Dict[str, Any],
                           preserve: List[PreserveDecision],
                           remove: List[RemoveDecision],
                           improve: List[ImproveDecision],
                           layout_strategy: LayoutStrategy) -> str:
        """Generate overall reasoning for the strategy"""
        
        reasoning_parts = []
        
        # Layout reasoning
        reasoning_parts.append(f"Layout strategy: {layout_strategy.reasoning}")
        
        # Preservation reasoning
        if preserve:
            reasoning_parts.append(
                f"Preserving {len(preserve)} key elements to maintain brand continuity"
            )
        
        # Removal reasoning
        if remove:
            reasoning_parts.append(
                f"Removing {len(remove)} elements that reduce clarity or add noise"
            )
        
        # Improvement reasoning
        if improve:
            critical_count = sum(1 for i in improve if i.priority == Priority.CRITICAL)
            high_count = sum(1 for i in improve if i.priority == Priority.HIGH)
            reasoning_parts.append(
                f"Addressing {critical_count} critical and {high_count} high-priority improvements"
            )
        
        return " ".join(reasoning_parts)


# Convenience function for skill registration
def redesign_intelligence_skill(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skill function for redesign intelligence
    
    Args:
        profile: WebsiteDesignProfile as dictionary
        
    Returns:
        Dictionary representation of RedesignStrategy
    """
    engine = RedesignIntelligenceEngine()
    strategy = engine.analyze(profile)
    return strategy.to_dict()
