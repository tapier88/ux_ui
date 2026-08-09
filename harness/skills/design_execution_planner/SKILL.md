# Design Execution Planner Skill

## Overview

The Design Execution Planner converts design decisions into a precise TECHNICAL BUILD PLAN.

This skill transforms **WHAT we want to design** into **HOW to build it exactly**.

## Purpose

After the Design Resource Hub determines which resources to use, the Design Execution Planner creates a detailed blueprint that the Site Builder can follow deterministically.

## Input

- `WebsiteDesignProfile` - Brand and design identity
- `RepositoryResearchReport` - Existing code analysis
- `RedesignStrategy` - Redesign approach
- `DesignRecommendation` - Design recommendations
- `DesignResourceReport` - Selected resources and tools

## Output

- `DesignBuildPlan` - Complete technical build plan containing:
  - Project configuration
  - Design tokens (colors, typography, spacing, etc.)
  - Page architecture
  - Section plans
  - Component plans
  - Layout specifications
  - Asset requirements
  - Motion/animation plans
  - Responsive behavior
  - Accessibility requirements
  - Performance constraints
  - Implementation order
  - Resource usage decisions
  - Migration plan (for existing projects)

## Key Features

### Design Tokens Generation

Generates comprehensive design tokens for:
- Colors (primary, secondary, accent, background, surface, text, muted, border, success, warning, error)
- Typography (font families, sizes, weights, line heights)
- Spacing (xs through xxxl)
- Border radii
- Shadows
- Borders
- Breakpoints
- Motion durations and easings
- Z-index layers

### Page Architecture

Creates `PagePlan` objects defining:
- Route
- Purpose
- Sections sequence
- Primary and secondary CTAs
- Navigation structure
- Footer requirements
- SEO requirements

### Section Planning

Creates `SectionPlan` objects with:
- Unique ID and name
- Purpose
- Layout type (asymmetric, editorial, overlapping, immersive, bento, full_bleed, layered, diagonal, storytelling, experimental, split, centered, grid, horizontal, sticky)
- Content structure
- Components required
- Assets needed
- Background specification
- Typography settings
- Motion effects
- Responsive behavior
- Accessibility considerations
- Performance priority

### Component Planning

Creates `ComponentPlan` objects specifying:
- Component identity and type
- Purpose
- Source resource (react-bits, shadcn, motion, custom, etc.)
- Variants
- Props interface
- States
- Responsive behavior
- Accessibility requirements
- Animation details
- Dependencies
- Inspiration source and adaptation reason (for externally inspired components)

### Layout Planning

Defines explicit layout specifications:
- Container width
- Grid system
- Column count
- Gaps (row and column)
- Alignment
- Positioning
- Layering
- Overlap settings
- Z-index assignments
- Image and text positioning
- Content density
- White space strategy

### Asset Planning

Creates `AssetPlan` objects for each asset:
- Asset ID and type (image, illustration, icon, video, 3d, background, texture, logo)
- Purpose
- Source or generation requirement
- Generator specification (for Higgsfield integration)
- Dimensions and aspect ratio
- Format
- Priority
- Optimization settings

For generative assets, creates `GenerationRequest` with:
- Asset type
- Creative direction
- Composition
- Style
- Aspect ratio
- Resolution
- Purpose

### Motion Planning

Creates `MotionPlan` objects specifying:
- Target element
- Trigger (scroll, hover, click, load, etc.)
- Animation type (fade, slide, scale, reveal, parallax, sticky, pin, scrub, stagger, horizontal, transform)
- Duration and delay
- Easing function
- From/to states
- Scrub and pin settings
- Stagger timing
- Priority
- Mobile behavior
- Reduced motion behavior
- Resource selection (Motion, GSAP, CSS)

Respects Design Resource Hub decisions for motion libraries.

### Responsive Planning

Creates `ResponsivePlan` with behavior for desktop, tablet, and mobile:
- Layout changes
- Font adjustments
- Spacing modifications
- Image adaptations
- Animation changes
- Visibility toggles
- Interaction changes

Considers mobile from the start, not as an afterthought.

### Accessibility Planning

Defines accessibility requirements:
- Semantic HTML usage
- Keyboard navigation
- Focus states
- ARIA attributes
- Color contrast ratios
- Reduced motion support
- Screen reader compatibility
- Touch target sizes
- Form accessibility

### Performance Planning

Sets performance constraints:
- Image optimization (formats, lazy loading, quality)
- Code splitting strategy
- Font loading strategy
- Animation budget
- Third-party dependency limits
- 3D budget
- Video budget
- Bundle size budgets

Can reject visually expensive techniques if performance cost is excessive.

### Implementation Order

Creates sequenced `ImplementationStep` objects:
1. Project setup
2. Design tokens
3. Typography
4. Global layout
5. Navigation
6. Hero
7. Content sections
8. Interactions
9. Responsive adaptations
10. Accessibility
11. Performance optimization
12. Quality validation

Each step includes:
- Order
- Task description
- Dependencies
- Files to create/modify
- Components involved
- Validation criteria

### File Planning

Predicts file structure needed by Site Builder:
```
src/
  components/
  sections/
  layouts/
  hooks/
  animations/
  styles/
  assets/
```

Adapts to existing project architecture when redsigning.

### Existing Code Awareness

For redesigns of existing projects:
- Distinguishes PRESERVE, MODIFY, REPLACE, CREATE, REMOVE actions
- Creates `MigrationPlan` with:
  - Items to preserve
  - Items to modify
  - Items to replace
  - Items to remove
  - Items to create
- Each item includes reason, risk level, and dependencies

Never rebuilds from scratch without justification.

### Resource Usage Tracking

Records exactly which resources will be used:
- Tailwind: YES/NO with reason
- shadcn: YES/NO with reason
- Motion: YES/NO with reason
- GSAP: YES/NO with reason
- Lenis: YES/NO with reason
- Three.js: YES/NO with reason
- React Bits: YES/NO with reason

Every decision includes justification.

### Design Diversity

Supports diverse layout types to avoid predictable patterns:
- Does NOT default to "text left + image right" everywhere
- Supports asymmetric, editorial, overlapping, immersive, bento, full_bleed, layered, diagonal, storytelling, experimental layouts

## Graph Integration

Uses the existing Graph Engine with nodes:
- `DesignPlanningNode`
- `PagePlanningNode`
- `SectionPlanningNode`
- `ComponentPlanningNode`
- `AssetPlanningNode`
- `MotionPlanningNode`
- `ResponsivePlanningNode`
- `AccessibilityPlanningNode`
- `PerformancePlanningNode`
- `BuildPlanValidationNode`

## State Management

Registers states:
- `DESIGN_PLAN_STARTED`
- `PAGE_PLAN_CREATED`
- `SECTION_PLAN_CREATED`
- `COMPONENT_PLAN_CREATED`
- `ASSET_PLAN_CREATED`
- `MOTION_PLAN_CREATED`
- `RESPONSIVE_PLAN_CREATED`
- `BUILD_PLAN_VALIDATED`
- `DESIGN_PLAN_FAILED`

## Events

Emits events via the Event System:
- Checkpoint creation events
- Plan validation events

## Checkpoints

Creates checkpoints:
- `DESIGN_PLAN_CREATED`
- `COMPONENT_PLAN_CREATED`
- `ASSET_PLAN_CREATED`
- `MOTION_PLAN_CREATED`
- `BUILD_PLAN_READY`

## Quality Gates

Before allowing Site Builder to begin, verifies:
- DesignBuildPlan is valid
- No unnecessary dependencies
- Responsive plan defined
- Accessibility plan defined
- Performance plan defined
- Asset plan defined
- Motion plan defined
- Implementation order defined
- Resource decisions justified

## Security

Does NOT store:
- API keys
- Tokens
- Cookies
- Passwords
- Credentials

## Usage

```python
from harness.skills.design_execution_planner import DesignExecutionPlanner

planner = DesignExecutionPlanner()

# Create build plan from design inputs
build_plan = planner.create_build_plan(
    design_profile=website_design_profile,
    redesign_strategy=redesign_strategy,
    resource_report=design_resource_report
)

# Validate the plan
is_valid, errors = build_plan.validate()

# Convert to dictionary for Site Builder
plan_dict = build_plan.to_dict()
```

## Files

- `__init__.py` - Module initialization and skill registration
- `SKILL.md` - This documentation
- `models.py` - Data models
- `planner.py` - Main planner orchestration
- `component_planner.py` - Component planning logic
- `layout_planner.py` - Layout specifications
- `motion_planner.py` - Animation planning
- `asset_planner.py` - Asset requirements
- `responsive_planner.py` - Responsive behavior
- `accessibility_planner.py` - Accessibility requirements
- `performance_planner.py` - Performance constraints
- `validation.py` - Plan validation
