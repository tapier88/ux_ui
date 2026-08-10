# Tapiero UX/UI Agent — Autonomous Web Design Harness

## Overview

An autonomous agent that redesigns real websites end-to-end: it inspects
an existing site, extracts what to preserve vs. improve, consults real
design resources and methodology, plans a technical build, and executes
real code changes with rollback safety. Every redesign is scored against
a quality gate before it's considered ready to ship.

This is **not** a template generator. The design philosophy — and the
reason each piece below exists — is documented in
[`ARCHITECTURE_PRINCIPLES.md`](./ARCHITECTURE_PRINCIPLES.md): the agent
builds outward from a client's *real* brand data and real design
methodology, never from a generic AI default. See
[`ROADMAP.md`](./ROADMAP.md) for the full plan and current status of
every phase.

## The pipeline

```
Website Intelligence      → inspects an existing site/project
        ↓
Redesign Intelligence     → decides what to preserve/remove/improve,
                             generates a real color palette from the
                             brand's own colors (color_intelligence.py)
        ↓
Design Resource Hub       → selects real frameworks/libraries, and
                             consults design-methodology references
                             (design_language.py) — grid systems,
                             typography rules, motion physics
        ↓
Design Execution Planner  → converts decisions into a technical build
                             plan: layout, design tokens, components,
                             motion, responsive/accessibility/perf plans
        ↓
Site Builder              → executes the plan as real file changes,
                             with checkpoints and automatic rollback
                             on failure
        ↓
Governance Gate           → scores the result (brand alignment,
                             accessibility, visual craft, performance,
                             SEO, originality) — blocks anything below
                             threshold, no exceptions
        ↓
Git Persistence           → commits and publishes, with validation
                             gates (see Task Completion Lifecycle below)
```

Wiring these into one executable graph (rather than callable
individually) is tracked as ROADMAP.md FASE 1 — not yet done.

## Repository layout

```
/workspace
├── harness/
│   ├── core/
│   │   ├── graph/          # Graph engine (nodes, edges, execution, cycle detection)
│   │   ├── state/          # Shared state + persistent checkpoint storage
│   │   ├── runtime/        # Runtime execution (timeout, max_steps, cancellation)
│   │   ├── governance/     # Elevation Scorer + Governance Gate
│   │   ├── events/         # Event system
│   │   └── git/            # Git persistence & publication
│   │
│   ├── memory/              # Cross-task persistent memory (brand profiles,
│   │                         # inspections, lessons learned, gate history)
│   ├── nodes/                # Graph node implementations
│   ├── tools/ , skills/      # Tool/skill registries
│   ├── skills/
│   │   ├── website_intelligence/
│   │   ├── redesign_intelligence/   # includes color_intelligence.py
│   │   ├── design_resource_hub/     # includes design_language.py
│   │   ├── design_execution_planner/
│   │   └── site_builder/
│   └── tests/
│
├── .env.example
├── README.md                  # This file
├── ARCHITECTURE.md            # Base harness engine details (graph/state/runtime)
├── ARCHITECTURE_PRINCIPLES.md # Governance philosophy — read this first
├── ROADMAP.md                 # Full phased plan + status
└── GRAPH.md                   # Graph engine documentation
```

## Core infrastructure

- **Graph Engine**: nodes/edges, conditional branching (evaluated via each
  node's `condition_func`, matched against edge labels), cycle detection.
- **State Engine**: per-task state with checkpoints; checkpoints can be
  persisted to disk (`harness/core/state/storage.py`) and a task can be
  reconstructed after a process restart.
- **Runtime**: per-node timeout, `max_steps` guard against routing bugs
  or unintended loops, cooperative cancellation.
- **Memory**: `harness/memory/` — JSONL-backed, thread-safe, queryable by
  subject/category/tags. This is what lets the agent reuse a brand
  profile or an inspection instead of redoing the work every task.
- **Governance**: `harness/core/governance/` — every redesign is scored
  on weighted signals with a hard floor per dimension (you cannot offset
  broken accessibility with a great color palette), and every evaluation
  (pass or fail) is recorded to memory.
- **Git Persistence**: commit/publish with validation gates — see Task
  Completion Lifecycle below.

## Task Completion Lifecycle

A task can only be marked **COMPLETE** after passing through:

```
IMPLEMENTING → TESTING → READY_TO_COMMIT → COMMITTED →
READY_TO_PUBLISH → PUBLISHED → VERIFIED → COMPLETE
```

Critical rules: tests must pass before any commit; no sensitive files
(.env, tokens, credentials) are ever committed; every commit must be
published to remote and the remote commit verified. If publication
isn't possible, the task stays `PUBLICATION_REQUIRED` and is never
marked complete.

## Quick start

```bash
# Full base-harness test suite
python -m harness.tests.run_all_tests

# Individual skill/module suites
python -m unittest harness.tests.test_git_persistence
python -m unittest harness.tests.test_runtime_fixes
python -m unittest harness.tests.test_checkpoint_persistence
python -m unittest harness.tests.test_memory
python -m unittest harness.tests.test_governance
python -m unittest harness.tests.test_color_intelligence
python -m unittest harness.tests.test_design_language
python -m unittest harness.tests.test_design_execution_planner
python -m unittest harness.tests.test_design_resource_hub
python -m unittest harness.tests.test_site_builder
python -m harness.tests.test_website_intelligence
python -m unittest harness.tests.test_redesign_intelligence
```

## Status

See `ROADMAP.md` for the authoritative, checkbox-tracked status of every
phase. In short: the 5-skill pipeline exists and each skill is now
individually tested; governance, memory, and color intelligence are
built; end-to-end graph orchestration (FASE 1) and client-facing
capabilities — prospecting, brand DNA extraction from a URL/images,
outreach — are still ahead.

## License

MIT
