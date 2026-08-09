# Site Builder Skill

## Overview

The Site Builder is a skill for the autonomous web design agent that executes design plans and converts them into real code modifications on a project. It takes WebsiteDesignProfile, RedesignStrategy, DesignResourceReport, and DesignBuildPlan as inputs and produces actual code changes.

## Purpose

The Site Builder:
1. Inspects existing projects to understand structure and architecture
2. Takes snapshots of project state before modifications
3. Consumes DesignBuildPlan from Design Execution Planner
4. Executes the plan without making independent design decisions
5. Manages file ownership (PRESERVE, MODIFY, REPLACE, CREATE, REMOVE)
6. Implements design tokens, components, sections, and layouts
7. Handles responsive, motion, accessibility, and performance requirements
8. Validates builds, syntax, types, and quality
9. Supports rollback on failure
10. Generates comprehensive build reports

## Architecture

```
WEBSITE
    ↓
WEBSITE INTELLIGENCE
    ↓
REDESIGN INTELLIGENCE
    ↓
DESIGN RESOURCE HUB
    ↓
DESIGN ENGINE
    ↓
DESIGN EXECUTION PLANNER
    ↓
SITE BUILDER ← This skill
    ↓
CODE MODIFICATION
    ↓
LOCAL VALIDATION
    ↓
VISUAL VALIDATION
    ↓
AI QUALITY CHECK
    ↓
PERFORMANCE CHECK
    ↓
ACCESSIBILITY CHECK
    ↓
FINAL BUILD
```

## Files

- `__init__.py` - Module exports and skill registration
- `SKILL.md` - This documentation
- `models.py` - Data models (ProjectSnapshot, CodeChange, BuildReport, etc.)
- `builder.py` - Main SiteBuilder class orchestrating the build process
- `project_inspector.py` - Project inspection and framework detection
- `file_manager.py` - File operations and ownership management
- `code_generator.py` - Code generation utilities
- `code_modifier.py` - Safe code modification with diff analysis
- `component_builder.py` - Component creation and reuse logic
- `section_builder.py` - Section implementation
- `asset_manager.py` - Asset handling and Higgsfield abstraction
- `dependency_manager.py` - Dependency detection and installation
- `validation.py` - Validation pipeline (build, syntax, types, etc.)
- `rollback.py` - Checkpoint and rollback functionality
- `diff_analyzer.py` - Diff safety analysis

## Core Principles

### INSPECT → PLAN → MODIFY → VALIDATE → REVIEW → COMMIT

Never generate everything from scratch when reusable code exists.

### Execution Over Decision Making

The Site Builder executes the DesignBuildPlan. It does NOT make independent design decisions when a plan exists.

### Conflict Detection

If a technical conflict prevents plan execution, stop, register the conflict, and request a new decision from Planner/Design Engine.

## Key Features

### Project Inspection

Before modifying any project:
- Analyze package.json, src/, app/, pages/, components/, public/, assets/, styles/
- Detect framework (React, Next.js, Vite, Vue, Astro, HTML/CSS/JS)
- Identify build system, routing, dependencies
- Never assume a technology

### Project Snapshot

Create ProjectSnapshot with:
- framework, language, package_manager, build_tool
- entry_points, routes, components, pages
- styles, assets, dependencies, scripts
- existing_design_system, existing_architecture

### File Ownership

Classify files before modification:
- PRESERVE - Do not touch
- MODIFY - Update content
- REPLACE - Replace entirely
- CREATE - New file
- REMOVE - Delete (requires justification)

Never delete critical files without justification.

### Design Build Plan Consumption

Consume DesignBuildPlan without reinventing:
- layout, typography, colors, components, motion

The Site Builder executes; it does not redesign.

### Implementation Order

Follow DesignBuildPlan.implementation_order:
1. dependencies
2. tokens
3. global styles
4. typography
5. layout
6. navigation
7. sections
8. components
9. assets
10. interactions
11. responsive
12. accessibility
13. performance
14. validation

### Design Tokens

Implement tokens defined by Planner:
- Support CSS variables, Tailwind configuration, theme systems
- Do not create duplicate token systems if compatible one exists

### Component Builder

Create components from ComponentPlan respecting:
- name, props, variants, states
- responsive_behavior, accessibility, animation
- source_resource

### Component Reuse

Before creating a component:
1. Reuse existing
2. Adapt existing
3. Use project component
4. Use selected resource
5. Create custom

NO duplicating components.

### Section Builder

Implement SectionPlan respecting:
- layout, content, components, assets
- background, typography, motion, responsive_behavior

### Layout Execution

Implement exactly the Planner's decisions:
- grid, flex, absolute, sticky, overlap, layers, z-index
- full-bleed, asymmetric, editorial, bento, immersive, storytelling

Do NOT replace asymmetric compositions with generic text-left/image-right structures.

### Responsive Implementation

Implement desktop, tablet, mobile per ResponsivePlan.
Each section must have defined responsive behavior.

### Motion Implementation

Implement MotionPlan using selected technology:
- Motion → microinteractions
- GSAP → timelines/ScrollTrigger
- Lenis → smooth scrolling
- CSS → simple animations
- Three.js → 3D

Do NOT add libraries not selected by Resource Hub.

### Reduced Motion

All animations must respect prefers-reduced-motion:
- Deactivate, reduce, or simplify when appropriate

### Asset Management

Consume AssetPlan classifying:
- existing, generated, external, placeholder, missing

Do NOT use random images if plan requires specific visual direction.

### Higgsfield Abstraction

If AssetPlan contains generation_required=true and generator=higgsfield:
- Create GenerationTask
- Do NOT execute non-existent API
- Allow future Higgsfield connection

### Image Optimization

When possible:
- WebP, AVIF, responsive images, lazy loading
- width, height, compression

Avoid giant images, images without dimensions, duplicate assets.

### Dependency Manager

Before installing:
- Verify: already exists? necessary? in DesignBuildPlan?
- Consider: alternative without dependency? bundle impact? framework compatibility?

Do NOT automatically install GSAP, Three.js, Lenis, Motion if not selected.

### Package Manager

Detect automatically: npm, pnpm, yarn, bun
Use existing package manager. DO NOT change.

### Code Quality

Generated code must respect:
- Existing architecture, naming conventions, formatting
- Linting, TypeScript (when applicable)
- Component boundaries, reusability

### Code Modification

Create CodeChange with:
- file, operation, reason, before, after, risk

Operations: CREATE, MODIFY, DELETE, RENAME

### Diff Safety

Before applying changes:
- Generate diff
- Validate: syntax, imports, references, paths, dependencies

If destructive change exists:
- Mark HIGH_RISK
- Stop automatically if threshold exceeded

### Checkpoint

Create checkpoint before modifications:
- BUILD_CHECKPOINT_BEFORE_MODIFICATION
- Allow rollback

### Rollback

If after modification:
- build fails, tests fail, imports fail, runtime fails

Must be able to ROLLBACK to last safe checkpoint.

### Validation Pipeline

After building:
1. syntax check
2. type check
3. lint
4. unit tests
5. build
6. route validation
7. asset validation
8. accessibility validation
9. performance validation
10. visual validation
11. AI quality validation

### Build Validation

Execute existing project build script:
- Detect: npm run build, pnpm build, yarn build, bun run build
- Do NOT assume commands

### Error Recovery

If failure:
- Classify: SYNTAX_ERROR, TYPE_ERROR, IMPORT_ERROR, etc.
- Register: error, file, line, severity, possible_fix

Attempt automatic recovery only when change is safe and deterministic.

### Visual Validation

Create VisualValidationResult abstraction:
- Allow future browser/screenshot/visual comparison integration
- Analyze: alignment, spacing, overflow, responsive layout, missing assets, visual hierarchy

If no automated browser available:
- Register VISUAL_VALIDATION_PENDING
- Do NOT invent results

### AI Quality Validation

After building:
- Send result to AI Quality / AI Slop Detector
- Evaluate: originality, composition, typography, visual hierarchy, brand fit, genericness, repetition, effect overuse

If score below threshold:
- BUILD_REVIEW_REQUIRED

### Design Fidelity

Compare DesignBuildPlan against Implementation:
- Create DesignFidelityReport with layout_match, component_match, typography_match, color_match, motion_match, responsive_match, asset_match, accessibility_match

### Performance

Validate:
- bundle size, large assets, unused dependencies
- animation cost, 3D cost, video cost, font cost

If visual decision causes excessive cost:
- Register PERFORMANCE_WARNING
- Do NOT automatically remove design decision without justification

### Accessibility

Validate:
- semantic HTML, ARIA, keyboard navigation, focus
- contrast, alt text, forms, touch targets, reduced motion

### SEO

When applicable validate:
- title, description, headings, semantic structure
- image alt, canonical, Open Graph, structured data

Do NOT modify existing SEO without justification.

### Existing Code Preservation

In redesigns:
- DO NOT automatically delete: SEO, routing, analytics, business logic, forms, API integrations, authentication, database logic, tracking, accessibility

Goal: CHANGE VISUAL EXPERIENCE without destroying existing functionality.

### Business Logic Protection

Classify code:
- VISUAL vs BUSINESS_LOGIC

Site Builder prioritizes visual modifications.
Business logic only modified if DesignBuildPlan explicitly requires.

## Events

- BUILD_STARTED
- PROJECT_INSPECTED
- DEPENDENCY_CHECKED
- DEPENDENCY_ADDED
- FILE_CREATED
- FILE_MODIFIED
- FILE_REMOVED
- COMPONENT_CREATED
- SECTION_CREATED
- ASSET_ADDED
- MOTION_IMPLEMENTED
- RESPONSIVE_IMPLEMENTED
- BUILD_VALIDATED
- VISUAL_VALIDATION_COMPLETED
- QUALITY_CHECK_COMPLETED
- BUILD_FAILED
- ROLLBACK_STARTED
- ROLLBACK_COMPLETED
- BUILD_COMPLETED

## Checkpoints

- BUILD_INITIAL_CHECKPOINT
- BUILD_BEFORE_MODIFICATION
- BUILD_AFTER_STRUCTURE
- BUILD_AFTER_COMPONENTS
- BUILD_AFTER_MOTION
- BUILD_BEFORE_VALIDATION
- BUILD_VALIDATED

## Graph Integration

Nodes:
- ProjectInspectionNode
- BuildPreparationNode
- DependencyNode
- TokenImplementationNode
- ComponentBuildNode
- SectionBuildNode
- AssetBuildNode
- MotionBuildNode
- ResponsiveBuildNode
- AccessibilityBuildNode
- PerformanceBuildNode
- BuildValidationNode
- VisualValidationNode
- QualityValidationNode
- BuildCompletionNode

## Security

- NO API keys stored
- NO tokens, cookies, passwords, credentials
- NO destructive commands without validation
- NO rm -rf, format, disk operations, credential extraction
- NO file modification outside project workspace
- Validate all paths
- Prevent path traversal, absolute path escape, unauthorized modification

## Usage

### Basic Usage

```python
from harness.skills.site_builder import (
    SiteBuilder,
    ProjectInspector,
    BuildReport,
)

# Create builder
builder = SiteBuilder(project_path="/path/to/project")

# Inspect project
snapshot = builder.inspect_project()

# Execute build plan
report = builder.execute_build(design_build_plan)

print(report.build_status)
print(report.files_created)
```

### Via Skill Registry

```python
from harness.skills.site_builder import load_site_builder_skill
from harness.skills import get_skill_registry

# Load the skill
load_site_builder_skill()

# Execute via registry
registry = get_skill_registry()
result = registry.execute_skill("site-builder", data={
    "project_path": "/path/to/project",
    "design_build_plan": plan,
})
```

## Testing

Run tests via:
```bash
python -m pytest harness/tests/test_site_builder.py
```

Or include in full test suite:
```bash
python harness/tests/run_all_tests.py
```

## Models

### ProjectSnapshot
Project structure snapshot with framework, package_manager, build_tool, entry_points, routes, components, pages, styles, assets, dependencies, scripts.

### CodeChange
Code modification with file, operation, reason, before, after, risk.

### BuildError
Build error with error_type, message, file, line, severity, possible_fix.

### CheckpointInfo
Checkpoint with checkpoint_id, task_id, timestamp, description, files_snapshot.

### RollbackResult
Rollback result with success, checkpoint_id, files_restored, errors.

### DiffResult
Diff analysis with file, changes, additions, deletions, is_safe, risk_level.

### ValidationResult
Generic validation with validation_type, status, message, details, errors, warnings.

### VisualValidationResult
Visual validation (abstraction) with status, message, alignment_check, spacing_check, overflow_check.

### AIQualityResult
AI quality evaluation with originality, composition, typography, hierarchy, brand_fit, genericness, repetition, effect_overuse, overall_score.

### DesignFidelityReport
Fidelity report with layout_match, component_match, typography_match, color_match, motion_match, responsive_match, asset_match, accessibility_match.

### BuildReport
Final report with project, task_id, files_created, files_modified, build_status, tests_status, visual_validation, accessibility, performance, ai_quality, design_fidelity.

### GenerationTask
Asset generation task (Higgsfield abstraction) with task_id, generator, asset_type, creative_direction, style, composition, status.

## Integration Points

- Website Intelligence (input)
- Redesign Intelligence (input)
- Design Resource Hub (input)
- Design Engine (input)
- Design Execution Planner (input)
- Skill Registry
- Graph Engine
- State Engine
- Event System
- Git Persistence
