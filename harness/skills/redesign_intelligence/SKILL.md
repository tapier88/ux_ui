# Redesign Intelligence Skill

## Overview

The Redesign Intelligence skill transforms a `WebsiteDesignProfile` into a comprehensive `RedesignStrategy`. This is the core intelligence engine that makes design decisions about what to preserve, remove, improve, and how to approach the redesign.

## Purpose

This skill does **NOT** build the final website. Its responsibility is to decide:

- What to conserve (brand identity, valuable content, functional components)
- What to eliminate (unnecessary decoration, redundant elements, obsolete patterns)
- What to improve (visual hierarchy, accessibility, performance)
- What to reorganize (content flow, layout structure)
- What pattern to use (asymmetric, editorial, bento, etc.)
- What visual architecture to propose
- What components to utilize
- What problems from the original site must be solved

## Architecture

```
WebsiteDesignProfile
        ↓
REDESIGN INTELLIGENCE ENGINE
        ↓
RedesignStrategy
        ↓
[Design Engine V0.1]
        ↓
DesignRecommendation
```

## Engines

The skill comprises multiple specialized engines:

### Preserve Engine
Determines which elements should be maintained from the original site:
- Brand identity (logo, colors, value proposition)
- SEO structure
- Effective navigation patterns
- Accessible components
- Relevant content
- Functional components

### Remove Engine
Identifies elements that should be eliminated:
- Excessive shadows
- Arbitrary gradients
- Unnecessary animations
- Redundant content sections
- Repeated components
- Generic UI patterns
- Obsolete visual patterns

### Improvement Engine
Detects opportunities for enhancement across categories:
- Visual (density, contrast, hierarchy)
- Layout (variety, engagement)
- Typography (hierarchy, readability)
- Content (headlines, messaging)
- Conversion (CTAs, user flow)
- Accessibility (contrast, keyboard navigation)
- Performance (load times, optimization)
- Interaction (feedback states)
- Responsive (mobile experience)

### Layout Strategy Engine
Recommends layout patterns based on:
- Industry type
- Brand personality
- Content type
- Audience

Available patterns include: asymmetric, editorial, bento, centered, overlapping, immersive, split, diagonal, layered, full-bleed, storytelling, grid, experimental.

### Visual Strategy Engine
Analyzes and recommends:
- Visual density
- Negative space
- Contrast levels
- Depth
- Hierarchy
- Rhythm
- Repetition
- Composition
- Scale relationships
- Image/text ratio

### Typography Strategy Engine
Defines:
- Hierarchy (H1, H2, H3, body, caption)
- Font sizes (responsive clamp functions)
- Font weights
- Line length
- Line height
- Letter spacing
- Font combinations

### Color Strategy Engine
Establishes:
- Primary, secondary, accent colors
- Background and foreground
- Muted colors
- Semantic colors (success, warning, error, info)
- Brand preservation guidelines

### Component Strategy Engine
Determines component actions:
- Preserve
- Remove
- Modify
- Replace
- Create

Follows the **Minimum Sufficient Stack** principle.

### Motion Strategy Engine
Defines:
- Animation intensity (none, subtle, moderate, expressive)
- Duration ranges
- Animated vs static elements
- Performance priorities
- Accessibility considerations

### Content Hierarchy Engine
Organizes:
- Primary content
- Secondary content
- Tertiary content
- Content flow
- Fold strategy

### Performance Strategy Engine
Optimizes:
- Images (formats, compression, responsive)
- JavaScript (bundle size, code-splitting)
- Animations (GPU-accelerated transforms)
- Dependencies (auditing, tree-shaking)
- Fonts (display, subsetting)
- Lazy loading

### Accessibility Strategy Engine
Addresses:
- Contrast issues
- Focus management
- Keyboard navigation
- Semantic HTML
- ARIA requirements
- Motion sensitivity
- Touch targets

### Risk Engine
Identifies potential risks:
- Over-designing
- Brand dilution
- Performance degradation
- Accessibility gaps
- Content mismatch
- Mobile compromise

## Usage

```python
from harness.skills.redesign_intelligence import (
    RedesignIntelligenceEngine,
    RedesignStrategy
)

# Create engine
engine = RedesignIntelligenceEngine()

# Analyze profile
profile = {
    "industry": "tech",
    "brand": {
        "personality": "bold",
        "colors": {"primary": "#FF5722"}
    },
    "goals": ["conversion", "engagement"],
    "visual": {"density": "high", "contrast": "low"},
    # ... more profile data
}

strategy = engine.analyze(profile)

# Get structured output
print(strategy.project_summary)
print(strategy.preserve)
print(strategy.remove)
print(strategy.improve)
print(strategy.layout_strategy.recommended_pattern)
```

Or use the skill function:

```python
from harness.skills import load_skill

# Load the skill
from harness.skills.redesign_intelligence import redesign_intelligence_skill
load_skill("redesign-intelligence", redesign_intelligence_skill)

# Execute via registry
from harness.skills import get_skill_registry
registry = get_skill_registry()
result = registry.execute_skill("redesign-intelligence", profile={...})
```

## Models

All models are Pydantic-compatible dataclasses with `to_dict()` methods for serialization.

Key models:
- `RedesignStrategy` - Complete strategy output
- `PreserveDecision` - Element preservation decision
- `RemoveDecision` - Element removal decision
- `ImproveDecision` - Improvement recommendation
- `LayoutStrategy` - Layout recommendations
- `VisualStrategy` - Visual recommendations
- `TypographyStrategy` - Typography recommendations
- `ColorStrategy` - Color recommendations
- `ComponentStrategy` - Component recommendations
- `MotionStrategy` - Motion recommendations
- `ContentHierarchyStrategy` - Content organization
- `PerformanceStrategy` - Performance optimizations
- `AccessibilityStrategy` - Accessibility improvements
- `DesignRisk` - Identified risks

## Design Diversity

The engine is designed to produce varied outputs based on input profiles. It avoids defaulting to predictable patterns by considering:

- Industry context
- Brand personality
- Content type
- Audience characteristics
- Existing design qualities
- Conversion goals
- Visual personality

## Integration

This skill integrates with Design Engine V0.1 to produce `DesignRecommendation` objects that can eventually be consumed by a Site Builder.

## Version

V0.1 - Initial implementation
