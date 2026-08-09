# Design Resource Hub Skill

## Overview

The Design Resource Hub is a skill for the autonomous web design agent that provides a catalog of official design resources, tools, and libraries. It enables the agent to research, select, and justify design resources BEFORE designing or redesigning any website.

## Purpose

Before designing, the agent must:
1. Analyze the project requirements
2. Determine what resources are needed
3. Consult relevant resources from the catalog
4. Study patterns, components, and techniques
5. Compare alternatives
6. Select appropriate resources
7. Justify selection and rejection
8. Deliver results to Design Engine
9. Only then proceed to design

## Architecture

```
WEBSITE INTELLIGENCE
        ↓
REDESIGN INTELLIGENCE
        ↓
DESIGN RESOURCE HUB ← This skill
        ↓
RESOURCE RESEARCH
        ↓
RESOURCE SELECTION
        ↓
DESIGN RESEARCH REPORT
        ↓
DESIGN ENGINE
```

## Files

- `__init__.py` - Module exports
- `models.py` - Data models (DesignResource, ResourceDecision, etc.)
- `catalog.py` - Official resource catalog with 21+ resources
- `researcher.py` - Research logic based on project requirements
- `selector.py` - Resource selection and rejection logic
- `rules.py` - Selection rules including minimum sufficient stack
- `registry.py` - Skill registration functions

## Resource Types

- LIBRARY
- FRAMEWORK
- COMPONENT_LIBRARY
- ANIMATION_LIBRARY
- DESIGN_SYSTEM
- ASSET_LIBRARY
- GENERATION_SKILL
- QUALITY_SKILL
- RESEARCH_RESOURCE
- TOOL

## Official Resources Included

### Foundation/Styling
- Tailwind CSS (HIGH priority)
- Bootstrap (MEDIUM priority)

### Components
- shadcn/ui (VERY HIGH priority)
- Radix UI (HIGH priority)
- MUI (MEDIUM priority)
- Ant Design (MEDIUM priority)
- Chakra UI (MEDIUM priority)
- Mantine (MEDIUM priority)
- React Bits (VERY HIGH priority - for inspiration)
- Magic UI (VERY HIGH priority)

### Animation/Motion
- Motion (VERY HIGH priority)
- GSAP (VERY HIGH priority)
- Lenis (HIGH priority)
- Animate.css (LOW priority)

### 3D/Immersive
- Three.js (CONDITIONAL - only if 3D required)

### Iconography
- Lucide (HIGH priority)
- Font Awesome (MEDIUM priority)

### Typography
- Google Fonts (HIGH priority)

### Development
- Storybook (MEDIUM/HIGH priority)
- Front-End Checklist (HIGH priority)

### Design Resources
- Design Resources for Developers (MEDIUM priority)

### Special Skills
- Higgsfield (GENERATION_SKILL - image/video generation)
- AI Quality Detector (QUALITY_SKILL - detects AI-generated slop)

## Key Rules

### Minimum Sufficient Stack
Do not use unnecessary resources. For a simple landing page:
- Tailwind + shadcn + Motion may be sufficient
- Do NOT automatically add GSAP, Lenis, Three.js, Magic UI, React Bits

### Three.js Conditional Rule
DO NOT recommend Three.js if the project does not need 3D/WebGL.

### Inspiration vs Copy
React Bits and similar resources should be used for INSPIRATION, not copying:
- Study composition, interaction, animation, structure, behavior
- ADAPT to project needs
- Never copy branding, text, images, identity, or complete pages

## Usage

### Basic Usage

```python
from harness.skills.design_resource_hub import (
    DesignResourceCatalog,
    DesignResourceResearcher,
    ResourceSelector,
    DesignResourceResearchRequest,
)

# Create request
request = DesignResourceResearchRequest(
    project_type="landing_page",
    industry="technology",
    brand_personality="modern",
    visual_style="clean",
    animation_level="MEDIUM",
    interaction_level="MEDIUM",
    _3d_required=False,
)

# Research and select
catalog = DesignResourceCatalog()
selector = ResourceSelector(catalog)
report = selector.generate_report(request, task_id="my-task")

print(report.minimum_stack)
print(report.resources_selected)
```

### Via Skill Registry

```python
from harness.skills.design_resource_hub import load_design_resource_hub_skill
from harness.skills import get_skill_registry

# Load the skill
load_design_resource_hub_skill()

# Execute via registry
registry = get_skill_registry()
result = registry.execute_skill("design-resource-hub", data={
    "project_type": "landing_page",
    "animation_level": "HIGH",
})
```

## Models

### DesignResource
Represents a design resource with:
- id, name, type, category
- repository, official_url
- purpose, capabilities, strengths, limitations
- recommended_for, avoid_when
- technology, license, commercial_use
- research_priority, implementation_priority, status

### DesignResourceResearchRequest
Research request with:
- project_type, industry, brand_personality
- visual_style, layout_style
- animation_level, interaction_level
- _3d_required, asset_generation_required
- performance_priority, accessibility_priority
- originality_priority, mobile_priority

### ResourceDecision
Selection decision with:
- resource, selected, score, reason
- alternative, complexity, performance_cost
- accessibility_impact, visual_fit, project_fit
- confidence

### DesignInspiration
Extracted pattern with:
- source, resource, pattern
- description, why_relevant, adaptation
- complexity, performance, confidence

### DesignResourceReport
Final report with:
- project_analysis
- resources_consulted, resources_selected, resources_rejected
- patterns_found, animation_ideas, layout_ideas, component_ideas
- implementation_recommendations
- performance_notes, accessibility_notes, license_notes
- design_diversity_notes, confidence, minimum_stack

## Events

The skill integrates with the event system:
- RESOURCE_RESEARCH_STARTED
- RESOURCE_CONSULTED
- RESOURCE_SELECTED
- RESOURCE_REJECTED
- INSPIRATION_FOUND
- RESOURCE_RESEARCH_COMPLETED
- RESOURCE_RESEARCH_FAILED

## Checkpoints

- RESOURCE_RESEARCH_PLAN
- RESOURCE_RESEARCH_RESULTS
- RESOURCE_SELECTION_COMPLETE
- DESIGN_RESEARCH_READY

## Integration Points

- Website Intelligence (input)
- Redesign Intelligence (input)
- Design Engine (output)
- Skill Registry
- Graph Engine
- State Engine
- Event System

## Security

- NO API keys stored
- NO tokens saved
- NO credentials in resources.json
- NO secrets in logs, cache, or Git

## Testing

Run tests via:
```bash
python -m pytest harness/tests/test_design_resource_hub.py
```

Or include in full test suite:
```bash
python harness/tests/run_all_tests.py
```
