# Redesign Intelligence Skill

## Overview

The Redesign Intelligence skill transforms a `WebsiteDesignProfile` into a comprehensive `RedesignStrategy`. This skill analyzes existing website designs and produces actionable recommendations for what to preserve, remove, improve, and how to approach the visual redesign.

## Purpose

This skill is part of the Harness design pipeline:

```
WEBSITE → WEBSITE INTELLIGENCE → WebsiteDesignProfile → REDESIGN INTELLIGENCE → RedesignStrategy → DESIGN ENGINE → DesignRecommendation
```

## What It Does

The Redesign Intelligence Engine:

1. **Analyzes** the existing website design profile
2. **Decides** what elements to preserve, remove, or improve
3. **Generates** strategies for layout, visual design, typography, color, components, motion, accessibility, and performance
4. **Identifies** potential risks
5. **Recommends** patterns and resources

## What It Does NOT Do

- Generate actual website code (React, HTML, CSS)
- Build the final site
- Replace the Design Engine

## Usage

### Loading the Skill

```python
from harness.skills import load_skill
from harness.skills.redesign_intelligence import run_redesign_intelligence

# Load the skill into the registry
load_skill("redesign-intelligence", run_redesign_intelligence)

# Or use directly
result = run_redesign_intelligence(profile)
```

### Input: WebsiteDesignProfile

The skill accepts a dictionary representing the website design profile:

```python
profile = {
    "brand": {
        "name": "Acme Corp",
        "personality": "modern",
        "primary_color": "#0066CC"
    },
    "industry": "technology",
    "content": {
        "sections": [
            {"type": "hero", "title": "Welcome", "priority": "high"},
            {"type": "features", "title": "Features", "priority": "medium"}
        ],
        "value_proposition": "Fast, reliable solutions"
    },
    "visual": {
        "density": "medium",
        "contrast": "high"
    },
    "typography": {
        "hierarchy": {"H1": "Display", "H2": "Section", "body": "Text"}
    },
    "accessibility": {
        "contrast_ratio": 4.5,
        "keyboard_accessible": True
    }
}
```

### Output: RedesignStrategy

The skill returns a structured strategy:

```python
{
    "project_summary": "Redesign strategy for Acme Corp in the technology sector",
    "original_analysis": "Brand: Acme Corp; Industry: technology; ...",
    "preserve": [
        {"element": "brand_identity", "reason": "...", "confidence": 0.95}
    ],
    "remove": [
        {"element": "visual_clutter", "reason": "...", "confidence": 0.50}
    ],
    "improve": [
        {
            "category": "visual",
            "current_state": "...",
            "problem": "...",
            "proposed_change": "...",
            "expected_benefit": "...",
            "priority": "high"
        }
    ],
    "layout_strategy": {
        "pattern": "asymmetric",
        "description": "...",
        "reasoning": "..."
    },
    "visual_strategy": {...},
    "typography_strategy": {...},
    "color_strategy": {...},
    "component_strategy": {...},
    "motion_strategy": {...},
    "content_hierarchy": {...},
    "performance_strategy": {...},
    "accessibility_strategy": {...},
    "risks": [...],
    "recommended_patterns": ["asymmetric"],
    "recommended_resources": ["shadcn/ui", "Lucide"],
    "confidence": 0.75,
    "reasoning": "..."
}
```

## Engines

The skill comprises multiple specialized engines:

### Preserve Engine
Identifies elements worth keeping from the original design:
- Brand identity (logo, name, colors)
- Value proposition
- Navigation structure
- SEO-critical content
- Accessible components
- Functional components

### Remove Engine
Detects elements that should be eliminated:
- Excessive shadows
- Arbitrary gradients
- Unnecessary animations
- Redundant content sections
- Purposeless decoration
- Generic UI patterns

### Improvement Engine
Finds opportunities across 9 categories:
- Visual
- Layout
- Typography
- Content
- Conversion
- Accessibility
- Performance
- Interaction
- Responsive

### Layout Strategy Engine
Selects from 13 layout patterns based on industry and brand personality:
- asymmetric, editorial, bento, centered, overlapping
- immersive, split, diagonal, layered, full-bleed
- storytelling, grid, experimental

### Visual Strategy Engine
Analyzes and recommends:
- Density levels
- Negative space usage
- Contrast levels
- Depth and hierarchy
- Rhythm and composition

### Typography Strategy Engine
Determines:
- H1/H2/H3 hierarchy
- Font sizes and weights
- Line length and height
- Letter spacing

### Color Strategy Engine
Preserves brand identity while recommending:
- Primary, secondary, accent colors
- Background and foreground
- Semantic colors (success, warning, error)

### Component Strategy Engine
Decides which components to:
- Preserve
- Remove
- Modify
- Replace
- Create

Follows the Minimum Sufficient Stack principle.

### Motion Strategy Engine
Recommends:
- Where to use animation
- Where to avoid it
- Intensity and duration
- Accessibility considerations

### Content Hierarchy Engine
Organizes content by priority:
- Primary (above fold)
- Secondary
- Tertiary

### Performance Strategy Engine
Optimizes:
- Images
- JavaScript
- Fonts
- Animations
- Dependencies

### Accessibility Strategy Engine
Ensures WCAG AA compliance:
- Contrast ratios
- Focus management
- Keyboard navigation
- Semantic HTML
- ARIA recommendations

### Risk Engine
Identifies potential issues:
- User alienation from radical changes
- Performance impacts
- Legal compliance risks
- ROI concerns

## Design Diversity

The engine avoids producing identical designs by considering:
- Industry context
- Brand personality
- Content type
- Existing design characteristics

This prevents the predictable pattern:
```
Hero (text left, image right) → 3 cards → CTA → Footer
```

## Integration

The output is compatible with the Design Engine V0.1:

```
WebsiteDesignProfile → RedesignStrategy → DesignEngine → DesignRecommendation
```

## Testing

Run tests with:

```bash
cd /workspace/harness/tests
python -m pytest test_redesign_intelligence.py -v
```

## Models

Key dataclasses:
- `PreserveDecision`
- `RemoveDecision`
- `ImproveDecision`
- `LayoutStrategy`
- `VisualStrategy`
- `TypographyStrategy`
- `ColorStrategy`
- `ComponentStrategy`
- `MotionStrategy`
- `ContentHierarchyStrategy`
- `PerformanceStrategy`
- `AccessibilityStrategy`
- `DesignRisk`
- `RedesignStrategy`

All models include `to_dict()` methods for serialization.
