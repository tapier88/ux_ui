"""
Design Resource Catalog - Official catalog of design resources
"""
import json
from typing import Dict, List, Optional, Any
from .models import DesignResource, ResourceType, ResourceCategory, ResourceStatus


class DesignResourceCatalog:
    """Catalog of official design resources"""

    def __init__(self):
        self._resources: Dict[str, DesignResource] = {}
        self._load_official_resources()

    def _load_official_resources(self):
        """Load the official catalog of resources"""
        
        # FOUNDATION / STYLING
        
        # 1. Tailwind CSS
        self.add_resource(DesignResource(
            id="tailwind-css",
            name="Tailwind CSS",
            type=ResourceType.FRAMEWORK,
            category=ResourceCategory.STYLING,
            repository="https://github.com/tailwindlabs/tailwindcss",
            official_url="https://tailwindcss.com/",
            purpose="Utility-first CSS framework for rapid UI development",
            capabilities=[
                "utility CSS",
                "responsive design",
                "design tokens",
                "layouts",
                "customization"
            ],
            strengths=[
                "fast development",
                "consistent design",
                "small bundle with purging",
                "highly customizable"
            ],
            limitations=[
                "learning curve for utility classes",
                "HTML can become verbose"
            ],
            recommended_for=[
                "modern web applications",
                "landing pages",
                "dashboards",
                "responsive designs"
            ],
            avoid_when=[
                "projects requiring traditional CSS architecture",
                "teams unfamiliar with utility-first approach"
            ],
            technology=["CSS", "PostCSS", "JavaScript"],
            license="MIT",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # 2. Bootstrap
        self.add_resource(DesignResource(
            id="bootstrap",
            name="Bootstrap",
            type=ResourceType.FRAMEWORK,
            category=ResourceCategory.STYLING,
            repository="https://github.com/twbs/bootstrap",
            official_url="https://getbootstrap.com/",
            purpose="Popular CSS framework for responsive UI components",
            capabilities=[
                "responsive UI",
                "CSS components",
                "JavaScript plugins",
                "grid system"
            ],
            strengths=[
                "wide adoption",
                "extensive documentation",
                "large component library",
                "easy to use"
            ],
            limitations=[
                "can look generic",
                "larger bundle size",
                "customization requires effort"
            ],
            recommended_for=[
                "prototypes",
                "admin dashboards",
                "quick projects"
            ],
            avoid_when=[
                "highly custom designs required",
                "performance-critical applications"
            ],
            technology=["CSS", "JavaScript", "Sass"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # COMPONENTS

        # 3. shadcn/ui
        self.add_resource(DesignResource(
            id="shadcn-ui",
            name="shadcn/ui",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/shadcn-ui/ui",
            official_url="https://ui.shadcn.com/",
            purpose="Beautifully designed React components that you can copy and paste",
            capabilities=[
                "React components",
                "UI modern",
                "accessibility",
                "composition",
                "Tailwind CSS based"
            ],
            strengths=[
                "copy-paste architecture",
                "full control over code",
                "beautiful defaults",
                "accessible by default",
                "built on Radix UI"
            ],
            limitations=[
                "requires manual setup",
                "not a traditional npm package",
                "React only"
            ],
            recommended_for=[
                "modern React applications",
                "landing pages",
                "dashboards",
                "design systems"
            ],
            avoid_when=[
                "non-React projects",
                "projects needing pre-bundled components"
            ],
            technology=["React", "TypeScript", "Tailwind CSS", "Radix UI"],
            license="MIT",
            commercial_use=True,
            research_priority="VERY HIGH",
            implementation_priority="VERY HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # 4. Radix UI
        self.add_resource(DesignResource(
            id="radix-ui",
            name="Radix UI",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/radix-ui/primitives",
            official_url="https://www.radix-ui.com/",
            purpose="Unstyled, accessible UI primitives for React",
            capabilities=[
                "primitives",
                "accessibility",
                "dialogs",
                "menus",
                "popovers",
                "interactions"
            ],
            strengths=[
                "fully accessible",
                "unstyled - full design control",
                "composable",
                "well-tested"
            ],
            limitations=[
                "requires styling knowledge",
                "more setup than styled components"
            ],
            recommended_for=[
                "custom design systems",
                "accessible applications",
                "complex interactions"
            ],
            avoid_when=[
                "need pre-styled components",
                "quick prototypes without accessibility needs"
            ],
            technology=["React", "TypeScript"],
            license="MIT",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # 5. MUI (Material-UI)
        self.add_resource(DesignResource(
            id="mui",
            name="MUI",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/mui/material-ui",
            official_url="https://mui.com/",
            purpose="React UI library implementing Material Design",
            capabilities=[
                "enterprise UI",
                "dashboards",
                "forms",
                "components",
                "theming"
            ],
            strengths=[
                "comprehensive component library",
                "Material Design implementation",
                "strong theming system",
                "large community"
            ],
            limitations=[
                "Material Design look may not fit all brands",
                "bundle size",
                "customization complexity"
            ],
            recommended_for=[
                "enterprise applications",
                "dashboards",
                "admin panels"
            ],
            avoid_when=[
                "unique brand identity required",
                "minimal bundle size critical"
            ],
            technology=["React", "TypeScript", "CSS-in-JS"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # 6. Ant Design
        self.add_resource(DesignResource(
            id="ant-design",
            name="Ant Design",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/ant-design/ant-design",
            official_url="https://ant.design/",
            purpose="Enterprise-class UI design language and React components",
            capabilities=[
                "enterprise components",
                "dashboards",
                "business applications",
                "data tables",
                "forms"
            ],
            strengths=[
                "comprehensive enterprise components",
                "excellent data tables",
                "professional look",
                "strong form handling"
            ],
            limitations=[
                "distinctive Ant Design look",
                "large bundle",
                "primarily for enterprise apps"
            ],
            recommended_for=[
                "enterprise applications",
                "B2B dashboards",
                "business tools"
            ],
            avoid_when=[
                "consumer-facing creative sites",
                "minimalist designs"
            ],
            technology=["React", "TypeScript", "Less"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # 7. Chakra UI
        self.add_resource(DesignResource(
            id="chakra-ui",
            name="Chakra UI",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/chakra-ui/chakra-ui",
            official_url="https://chakra-ui.com/",
            purpose="Simple, modular and accessible React components",
            capabilities=[
                "accessible components",
                "React UI",
                "design systems",
                "theming",
                "style props"
            ],
            strengths=[
                "accessibility first",
                "easy to use",
                "modular architecture",
                "good defaults"
            ],
            limitations=[
                "less flexible than headless libraries",
                "CSS-in-JS overhead"
            ],
            recommended_for=[
                "accessible applications",
                "rapid prototyping",
                "design systems"
            ],
            avoid_when=[
                "zero CSS-in-JS requirement",
                "extremely performance-critical apps"
            ],
            technology=["React", "TypeScript", "CSS-in-JS"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # 8. Mantine
        self.add_resource(DesignResource(
            id="mantine",
            name="Mantine",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/mantinedev/mantine",
            official_url="https://mantine.dev/",
            purpose="React components library with hooks and utilities",
            capabilities=[
                "React components",
                "hooks",
                "forms",
                "applications",
                "theming"
            ],
            strengths=[
                "comprehensive hooks library",
                "great form handling",
                "good documentation",
                "active development"
            ],
            limitations=[
                "smaller community than MUI",
                "CSS-in-JS approach"
            ],
            recommended_for=[
                "React applications",
                "dashboards",
                "forms-heavy apps"
            ],
            avoid_when=[
                "avoiding CSS-in-JS",
                "need maximum community support"
            ],
            technology=["React", "TypeScript", "CSS-in-JS"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # REACT / CREATIVE COMPONENTS

        # 9. React Bits
        self.add_resource(DesignResource(
            id="react-bits",
            name="React Bits",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/DavidHDev/react-bits",
            official_url="https://reactbits.dev/",
            purpose="Creative and animated React components for inspiration",
            capabilities=[
                "creative components",
                "animated components",
                "visual effects",
                "interaction ideas",
                "UI inspiration",
                "motion patterns"
            ],
            strengths=[
                "excellent for inspiration",
                "modern animations",
                "creative patterns",
                "copy-paste friendly",
                "Tailwind based"
            ],
            limitations=[
                "NOT for copying complete pages",
                "should be adapted, not copied directly",
                "some components may need customization"
            ],
            recommended_for=[
                "creative landing pages",
                "portfolio sites",
                "modern web apps",
                "pattern inspiration"
            ],
            avoid_when=[
                "copying entire page designs",
                "ignoring adaptation to brand",
                "simple content sites"
            ],
            technology=["React", "TypeScript", "Tailwind CSS", "Framer Motion"],
            license="MIT",
            commercial_use=True,
            research_priority="VERY HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE,
            metadata={
                "usage_note": "Use for INSPIRATION and COMPONENT PATTERNS. Study composition, interaction, animation, structure, behavior. ADAPT to project needs."
            }
        ))

        # 10. Magic UI
        self.add_resource(DesignResource(
            id="magic-ui",
            name="Magic UI",
            type=ResourceType.COMPONENT_LIBRARY,
            category=ResourceCategory.COMPONENTS,
            repository="https://github.com/magicuidesign/magicui",
            official_url="https://magicui.design/",
            purpose="Animated UI components for modern landing pages",
            capabilities=[
                "animated components",
                "modern landing pages",
                "visual effects",
                "React",
                "Tailwind",
                "Motion"
            ],
            strengths=[
                "stunning visual effects",
                "modern aesthetic",
                "well-documented",
                "Tailwind based"
            ],
            limitations=[
                "may be overkill for simple sites",
                "animation performance considerations"
            ],
            recommended_for=[
                "landing pages",
                "product launches",
                "modern SaaS sites",
                "creative portfolios"
            ],
            avoid_when=[
                "content-focused sites",
                "performance-critical low-end devices"
            ],
            technology=["React", "TypeScript", "Tailwind CSS", "Framer Motion"],
            license="MIT",
            commercial_use=True,
            research_priority="VERY HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # ANIMATION / MOTION

        # 11. Motion (formerly Framer Motion)
        self.add_resource(DesignResource(
            id="motion",
            name="Motion",
            type=ResourceType.ANIMATION_LIBRARY,
            category=ResourceCategory.ANIMATION,
            repository="https://github.com/motiondivision/motion",
            official_url="https://motion.dev/",
            purpose="Production-ready motion library for React",
            capabilities=[
                "React animation",
                "layout animation",
                "transitions",
                "gestures",
                "microinteractions",
                "viewport animations"
            ],
            strengths=[
                "declarative API",
                "layout animations",
                "gesture support",
                "performance optimized",
                "easy to learn"
            ],
            limitations=[
                "React only",
                "learning curve for advanced features"
            ],
            recommended_for=[
                "interactive React apps",
                "smooth transitions",
                "microinteractions",
                "page transitions"
            ],
            avoid_when=[
                "vanilla JavaScript projects",
                "simple static sites"
            ],
            technology=["React", "TypeScript", "JavaScript"],
            license="MIT",
            commercial_use=True,
            research_priority="VERY HIGH",
            implementation_priority="VERY HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # 12. GSAP
        self.add_resource(DesignResource(
            id="gsap",
            name="GSAP",
            type=ResourceType.ANIMATION_LIBRARY,
            category=ResourceCategory.ANIMATION,
            repository="https://github.com/greensock/GSAP",
            official_url="https://gsap.com/",
            purpose="Professional-grade animation library for web",
            capabilities=[
                "advanced animation",
                "timelines",
                "scroll animation",
                "ScrollTrigger",
                "parallax",
                "pinning",
                "scrub",
                "complex interactions"
            ],
            strengths=[
                "industry standard",
                "incredibly powerful",
                "excellent browser support",
                "ScrollTrigger plugin",
                "timeline control"
            ],
            limitations=[
                "commercial license for some uses",
                "steeper learning curve",
                "can be overkill for simple animations"
            ],
            recommended_for=[
                "complex animations",
                "scroll-based experiences",
                "interactive storytelling",
                "award-winning websites"
            ],
            avoid_when=[
                "simple fade-in animations needed",
                "budget constraints for commercial use"
            ],
            technology=["JavaScript", "TypeScript"],
            license="Standard Commercial / Open Source",
            commercial_use=False,  # Requires commercial license for some uses
            research_priority="VERY HIGH",
            implementation_priority="CONDITIONAL",
            status=ResourceStatus.ACTIVE,
            metadata={
                "license_note": "Free for most uses, but commercial products require paid license"
            }
        ))

        # 13. Lenis
        self.add_resource(DesignResource(
            id="lenis",
            name="Lenis",
            type=ResourceType.LIBRARY,
            category=ResourceCategory.ANIMATION,
            repository="https://github.com/darkroomengineering/lenis",
            official_url="https://lenis.darkroom.engineering/",
            purpose="Smooth scrolling library for enhanced scroll experience",
            capabilities=[
                "smooth scrolling",
                "scroll experience",
                "integration with GSAP",
                "scroll-based experiences"
            ],
            strengths=[
                "lightweight",
                "performant",
                "works well with GSAP ScrollTrigger",
                "natural feel"
            ],
            limitations=[
                "adds JS dependency for scroll",
                "may affect accessibility if not implemented carefully"
            ],
            recommended_for=[
                "premium scroll experiences",
                "parallax effects",
                "storytelling sites",
                "portfolio sites"
            ],
            avoid_when=[
                "content-heavy sites where native scroll is preferred",
                "accessibility-first projects without careful testing"
            ],
            technology=["JavaScript", "TypeScript"],
            license="MIT",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="CONDITIONAL",
            status=ResourceStatus.ACTIVE
        ))

        # 14. Animate.css
        self.add_resource(DesignResource(
            id="animate-css",
            name="Animate.css",
            type=ResourceType.ANIMATION_LIBRARY,
            category=ResourceCategory.ANIMATION,
            repository="https://github.com/animate-css/animate.css",
            official_url="https://animate.style/",
            purpose="Library of ready-to-use CSS animations",
            capabilities=[
                "CSS animations",
                "simple transitions",
                "basic animation"
            ],
            strengths=[
                "easy to use",
                "no JavaScript required",
                "wide variety of animations",
                "lightweight"
            ],
            limitations=[
                "limited customization",
                "generic animations",
                "less performant than JS for complex animations"
            ],
            recommended_for=[
                "simple animations",
                "quick prototypes",
                "basic transitions"
            ],
            avoid_when=[
                "complex animation sequences needed",
                "unique animation requirements"
            ],
            technology=["CSS"],
            license="MIT",
            commercial_use=True,
            research_priority="LOW",
            implementation_priority="LOW",
            status=ResourceStatus.ACTIVE
        ))

        # 3D / IMMERSIVE

        # 15. Three.js
        self.add_resource(DesignResource(
            id="three-js",
            name="Three.js",
            type=ResourceType.LIBRARY,
            category=ResourceCategory.THREE_D,
            repository="https://github.com/mrdoob/three.js",
            official_url="https://threejs.org/",
            purpose="JavaScript 3D library for WebGL",
            capabilities=[
                "WebGL",
                "3D",
                "immersive experiences",
                "interactive scenes",
                "3D visualization"
            ],
            strengths=[
                "powerful 3D rendering",
                "large ecosystem",
                "extensive examples",
                "active community"
            ],
            limitations=[
                "steep learning curve",
                "performance considerations",
                "larger bundle size",
                "requires 3D assets"
            ],
            recommended_for=[
                "3D product visualizations",
                "immersive experiences",
                "data visualization",
                "creative portfolios"
            ],
            avoid_when=[
                "project doesn't need 3D/WebGL",
                "performance-critical on low-end devices",
                "simple content sites"
            ],
            technology=["JavaScript", "WebGL", "TypeScript"],
            license="MIT",
            commercial_use=True,
            research_priority="CONDITIONAL",
            implementation_priority="CONDITIONAL",
            status=ResourceStatus.ACTIVE,
            metadata={
                "conditional_rule": "DO NOT recommend if project does not need 3D/WebGL"
            }
        ))

        # ICONOGRAPHY

        # 16. Lucide
        self.add_resource(DesignResource(
            id="lucide",
            name="Lucide",
            type=ResourceType.ASSET_LIBRARY,
            category=ResourceCategory.ICONOGRAPHY,
            repository="https://github.com/lucide-icons/lucide",
            official_url="https://lucide.dev/",
            purpose="Beautiful & consistent icon set",
            capabilities=[
                "interface icons",
                "clean iconography",
                "UI systems",
                "multiple frameworks"
            ],
            strengths=[
                "clean design",
                "consistent style",
                "open source",
                "framework integrations"
            ],
            limitations=[
                "smaller icon set than some alternatives",
                "single style"
            ],
            recommended_for=[
                "modern UIs",
                "clean interfaces",
                "React/Vue/Svelte apps"
            ],
            avoid_when=[
                "need varied icon styles",
                "require very specific icons not in set"
            ],
            technology=["SVG", "React", "Vue", "Svelte"],
            license="ISC",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # 17. Font Awesome
        self.add_resource(DesignResource(
            id="font-awesome",
            name="Font Awesome",
            type=ResourceType.ASSET_LIBRARY,
            category=ResourceCategory.ICONOGRAPHY,
            repository="https://github.com/FortAwesome/Font-Awesome",
            official_url="https://fontawesome.com/",
            purpose="Icon set and toolkit",
            capabilities=[
                "icons",
                "social icons",
                "interface icons",
                "web fonts",
                "SVG icons"
            ],
            strengths=[
                "massive icon library",
                "widely recognized",
                "easy integration",
                "free tier available"
            ],
            limitations=[
                "some icons require Pro license",
                "can look generic"
            ],
            recommended_for=[
                "social icons",
                "common UI icons",
                "quick integration"
            ],
            avoid_when=[
                "unique icon style required",
                "all icons needed are Pro-only"
            ],
            technology=["Web Fonts", "SVG", "React", "Vue"],
            license="CC BY 4.0 (Free) / Commercial (Pro)",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # TYPOGRAPHY

        # 18. Google Fonts
        self.add_resource(DesignResource(
            id="google-fonts",
            name="Google Fonts",
            type=ResourceType.ASSET_LIBRARY,
            category=ResourceCategory.TYPOGRAPHY,
            repository="https://github.com/google/fonts",
            official_url="https://fonts.google.com/",
            purpose="Free font library for web",
            capabilities=[
                "typography",
                "font pairing",
                "brand typography",
                "web fonts"
            ],
            strengths=[
                "free to use",
                "huge selection",
                "easy integration",
                "reliable CDN",
                "variable fonts support"
            ],
            limitations=[
                "popular fonts may feel common",
                "CDN dependency (privacy concerns)"
            ],
            recommended_for=[
                "any web project",
                "typography-focused designs",
                "brand identity"
            ],
            avoid_when=[
                "custom brand fonts needed",
                "offline-first applications"
            ],
            technology=["Web Fonts", "CSS"],
            license="Open Source (various)",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # DESIGN SYSTEM / DEVELOPMENT

        # 19. Storybook
        self.add_resource(DesignResource(
            id="storybook",
            name="Storybook",
            type=ResourceType.TOOL,
            category=ResourceCategory.DEVELOPMENT,
            repository="https://github.com/storybookjs/storybook",
            official_url="https://storybook.js.org/",
            purpose="Frontend workshop for UI development",
            capabilities=[
                "component development",
                "documentation",
                "visual testing",
                "design systems"
            ],
            strengths=[
                "isolated component development",
                "visual regression testing",
                "documentation generation",
                "addon ecosystem"
            ],
            limitations=[
                "setup complexity",
                "build time overhead"
            ],
            recommended_for=[
                "design systems",
                "component libraries",
                "team collaboration"
            ],
            avoid_when=[
                "small solo projects",
                "simple sites without reusable components"
            ],
            technology=["JavaScript", "TypeScript", "React", "Vue", "Angular"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # 20. Front-End Checklist
        self.add_resource(DesignResource(
            id="front-end-checklist",
            name="Front-End Checklist",
            type=ResourceType.RESEARCH_RESOURCE,
            category=ResourceCategory.DEVELOPMENT,
            repository="https://github.com/thedaviddias/Front-End-Checklist",
            official_url=None,
            purpose="Checklist for frontend quality assurance",
            capabilities=[
                "frontend quality",
                "accessibility",
                "performance",
                "SEO",
                "compatibility",
                "production readiness"
            ],
            strengths=[
                "comprehensive checklist",
                "best practices reference",
                "community maintained"
            ],
            limitations=[
                "not a tool, just a reference",
                "requires manual checking"
            ],
            recommended_for=[
                "production deployments",
                "quality assurance",
                "learning best practices"
            ],
            avoid_when=[],
            technology=["General Frontend"],
            license="MIT",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="HIGH",
            status=ResourceStatus.ACTIVE
        ))

        # DESIGN RESOURCES

        # 21. Design Resources for Developers
        self.add_resource(DesignResource(
            id="design-resources-for-developers",
            name="Design Resources for Developers",
            type=ResourceType.RESEARCH_RESOURCE,
            category=ResourceCategory.DESIGN_RESOURCES,
            repository="https://github.com/bradtraversy/design-resources-for-developers",
            official_url=None,
            purpose="Curated list of design and development resources",
            capabilities=[
                "design resources",
                "assets",
                "tools",
                "inspiration",
                "development resources"
            ],
            strengths=[
                "curated collection",
                "wide variety",
                "developer-focused"
            ],
            limitations=[
                "not a tool itself",
                "requires exploration"
            ],
            recommended_for=[
                "finding design assets",
                "discovering tools",
                "inspiration gathering"
            ],
            avoid_when=[],
            technology=["General"],
            license="MIT",
            commercial_use=True,
            research_priority="MEDIUM",
            implementation_priority="MEDIUM",
            status=ResourceStatus.ACTIVE
        ))

        # SPECIAL RESOURCES

        # Higgsfield - Generation Skill
        self.add_resource(DesignResource(
            id="higgsfield",
            name="Higgsfield",
            type=ResourceType.GENERATION_SKILL,
            category=ResourceCategory.AI_TOOLS,
            repository=None,
            official_url=None,
            purpose="AI-powered image and video generation for creative assets",
            capabilities=[
                "image generation",
                "video generation",
                "creative assets",
                "visual concepts",
                "campaign assets",
                "cinematic content"
            ],
            strengths=[
                "AI-powered generation",
                "creative flexibility",
                "rapid asset creation"
            ],
            limitations=[
                "external service",
                "API costs may apply",
                "quality varies by prompt"
            ],
            recommended_for=[
                "creative campaigns",
                "concept visualization",
                "asset generation"
            ],
            avoid_when=[
                "specific branded assets required",
                "legal/compliance restrictions on AI content"
            ],
            technology=["AI", "Generation"],
            license="Proprietary",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="PENDING",
            status=ResourceStatus.ACTIVE,
            metadata={
                "note": "External generation skill - treat as capability, not frontend library"
            }
        ))

        # AI Quality / AI Slop Detector
        self.add_resource(DesignResource(
            id="ai-quality-detector",
            name="AI Quality Detector",
            type=ResourceType.QUALITY_SKILL,
            category=ResourceCategory.QUALITY,
            repository=None,
            official_url=None,
            purpose="Detect AI-generated design patterns and quality issues",
            capabilities=[
                "detect generic design",
                "identify repetitive composition",
                "gradient overuse detection",
                "glassmorphism excess",
                "shadow overuse",
                "predictable layouts",
                "generic typography",
                "repeated components",
                "artificial aesthetics",
                "lack of identity",
                "effect overuse"
            ],
            strengths=[
                "quality improvement",
                "originality enhancement",
                "brand differentiation"
            ],
            limitations=[
                "subjective evaluation",
                "evolving detection criteria"
            ],
            recommended_for=[
                "quality assurance",
                "redesign intelligence",
                "design review"
            ],
            avoid_when=[],
            technology=["Analysis", "Evaluation"],
            license="Internal",
            commercial_use=True,
            research_priority="HIGH",
            implementation_priority="PENDING",
            status=ResourceStatus.PENDING_RESOURCE,
            metadata={
                "note": "PENDING_RESOURCE - May link to specific repo when identified"
            }
        ))

    def add_resource(self, resource: DesignResource) -> bool:
        """Add a resource to the catalog"""
        if resource.id in self._resources:
            return False
        self._resources[resource.id] = resource
        return True

    def get_resource(self, resource_id: str) -> Optional[DesignResource]:
        """Get a resource by ID"""
        return self._resources.get(resource_id)

    def get_resources_by_type(self, resource_type: ResourceType) -> List[DesignResource]:
        """Get all resources of a specific type"""
        return [r for r in self._resources.values() if r.type == resource_type]

    def get_resources_by_category(self, category: ResourceCategory) -> List[DesignResource]:
        """Get all resources of a specific category"""
        return [r for r in self._resources.values() if r.category == category]

    def get_resources_by_priority(self, priority: str) -> List[DesignResource]:
        """Get resources by research or implementation priority"""
        return [
            r for r in self._resources.values()
            if r.research_priority == priority or r.implementation_priority == priority
        ]

    def search_resources(self, query: str) -> List[DesignResource]:
        """Search resources by name, purpose, or capabilities"""
        query_lower = query.lower()
        results = []
        for resource in self._resources.values():
            if (query_lower in resource.name.lower() or
                query_lower in resource.purpose.lower() or
                any(query_lower in cap.lower() for cap in resource.capabilities)):
                results.append(resource)
        return results

    def list_all_resources(self) -> List[DesignResource]:
        """List all resources in the catalog"""
        return list(self._resources.values())

    def count_resources(self) -> int:
        """Count total resources in catalog"""
        return len(self._resources)

    def to_dict(self) -> Dict[str, Any]:
        """Convert catalog to dictionary"""
        return {
            "resources": {rid: r.to_dict() for rid, r in self._resources.items()},
            "count": len(self._resources)
        }

    def export_json(self, indent: int = 2) -> str:
        """Export catalog as JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
