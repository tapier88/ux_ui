# Architecture Documentation - Harness

## Overview

This repository contains a modular autonomous web-design harness. The current
system is no longer only the V0.1 base infrastructure: it now includes a real
design pipeline, governance gate, memory persistence, deterministic agent cycle,
and provider-agnostic creative judgment contract.

The execution model is graph-based. Work enters through `GraphRuntime`, moves
through typed nodes, stores state/checkpoints, emits events, and persists task
progress through Git when changes are ready to publish.

## Design Principles

1. **Modularity**: graph, state, runtime, tools, skills, agents, memory, and git
   persistence are separate modules.
2. **Provider abstraction**: LLM access is behind `LLMProvider`; creative
   judgments are behind `BaseDesignJudgmentEngine`.
3. **Deterministic safety first**: design execution can run in dry-run mode, and
   real writes are blocked by governance failures.
4. **Recoverability**: state checkpoints can be restored from memory or disk.
5. **Observability**: runtime events, stage outputs, governance evidence, and
   agent traces are inspectable.
6. **Publication discipline**: a task is not complete until changes are
   committed, pushed, and verified remotely.

## Directory Structure

```text
ux_ui/
|-- harness/
|   |-- agents/       # LLM providers, design judgment, deterministic agent loop
|   |-- core/
|   |   |-- events/   # Event model and emitter
|   |   |-- git/      # Git inspection, persistence, publication validation
|   |   |-- governance/ # Elevation scoring and blocking gate
|   |   |-- graph/    # Graph, Node, Edge, GraphBuilder
|   |   |-- runtime/  # GraphRuntime execution engine
|   |   |-- state/    # TaskState, checkpoints, file checkpoint storage
|   |   `-- time.py   # Timezone-aware UTC timestamps
|   |-- memory/       # JSONL memory store and categories
|   |-- nodes/        # Standard nodes and design pipeline nodes
|   |-- skills/       # Website/design intelligence and build skills
|   |-- tests/        # Unit and integration tests
|   `-- tools/        # Tool registry and mock tools
|-- projects/         # Project output area
|-- ARCHITECTURE.md
|-- ARCHITECTURE_PRINCIPLES.md
|-- GRAPH.md
|-- HARNESS_AUDIT.md
|-- PLAN.md
|-- README.md
`-- ROADMAP.md
```

## Core Runtime

### Graph Engine (`harness/core/graph/`)

Defines and validates directed workflows.

- `Graph`: node and edge container.
- `Node`: executable graph unit with id, name, type, and optional execute
  function.
- `Edge`: connection between nodes, including conditional/loop routing support.
- `NodeType`: `START`, `END`, `STANDARD`, `CONDITIONAL`, `LOOP`.
- `GraphBuilder`: fluent graph construction helper.

### State Engine (`harness/core/state/`)

Maintains task state across graph execution.

- `TaskState`: inputs, outputs, status, current node, history, and errors.
- `Checkpoint`: serializable state snapshot.
- `StateManager`: task state and checkpoint management.
- File checkpoint storage supports process-restart recovery.

### Runtime Engine (`harness/core/runtime/`)

Executes graphs with bounded safety controls.

- Sequential graph execution.
- Conditional routing.
- Loop handling with `max_steps`.
- Node timeout handling.
- Retry support.
- Checkpoint creation.
- Event emission.
- Correct task failure reporting when any node fails.

## Skills and Design Pipeline

### Skill Registry (`harness/skills/`)

Skills are reusable capabilities registered in the local registry. Current
design-relevant skills include:

- `prospecting`: ranks provided candidate websites by redesign opportunity
  without scraping or contacting leads.
- `website_intelligence`: inspects project structure and extracts a design
  profile.
- `redesign_intelligence`: decides what to preserve, remove, improve, and how to
  structure visual strategy.
- `design_resource_hub`: selects practical design resources for the project.
- `design_execution_planner`: creates `DesignBuildPlan`, including pages,
  sections, navigation, interactions, accessibility, performance, and style
  outputs.
- `seo_analysis`: evaluates metadata, social preview, semantic sections,
  indexability hints, and performance support before governance.
- `client_proposal`: generates client-facing Markdown with before/after,
  SEO impact, and quality proof.
- `site_builder`: writes actual implementation artifacts when execution is not
  dry-run.

### DesignPipelineNode (`harness/nodes/design_pipeline_node.py`)

Runs the full deterministic design flow:

```text
website_intelligence
-> redesign_intelligence
-> design_resource_hub
-> design_execution_planner
-> seo_analysis
-> governance_gate
-> client_proposal
-> site_builder
```

The node supports:

- dry-run execution;
- real build execution;
- explicit stage status;
- deterministic governance signals;
- blocked writes when quality gates fail.

## Governance

`harness/core/governance/` protects the pipeline from handing low-quality work
to the client or writing it as a real build.

- `ElevationSignal`: one scored quality dimension.
- `ElevationScorer`: weighted score and hard-fail logic.
- `GovernanceGate`: pass/block decision with evidence.

Current signal dimensions:

- `brand_alignment`
- `accessibility`
- `visual_craft`
- `performance`
- `seo_impact`
- `originality`

`DesignPipelineNode` derives these signals from concrete pipeline outputs
instead of invented numbers.

## Agents

### LLM Provider Adapter (`harness/agents/__init__.py`)

The provider layer remains interchangeable:

- `LLMProvider`: abstract provider contract.
- `MockLLMProvider`: default test-safe provider.
- `QwenAgentProvider`: placeholder for real Qwen credentials.
- `LLMAdapterFactory`: provider creation and caching.

### BaseDesignJudgmentEngine (`harness/agents/judgment.py`)

Creative judgments now have a provider-agnostic contract:

- `DesignJudgmentRequest`: judgment type, subject, criteria, context, metadata.
- `DesignJudgmentResult`: decision, rationale, confidence, provider status,
  raw response, metadata.
- `BaseDesignJudgmentEngine`: builds structured prompts, calls any
  `LLMProvider`, and normalizes the response.

This lets future skills swap mock/Qwen/other providers without changing their
public API.

### DeterministicDesignAgent (`harness/agents/design_cycle.py`)

The first Fase 3 agent layer wraps `DesignPipelineNode` in an auditable loop:

```text
PLAN -> EXECUTE -> OBSERVE -> EVALUATE -> DECIDE
```

Properties:

- first pass is always dry-run;
- real writes happen only after dry-run governance passes;
- `max_iterations` bounds replanning;
- retry currently handles over-strict governance thresholds safely;
- hard failures remain blocked.

### DesignAgentCycleNode (`harness/nodes/design_agent_cycle_node.py`)

Exposes the deterministic agent cycle as a normal graph node. It can be created
directly or through:

```python
create_node_factory()["design_agent_cycle"]
```

## Memory

`harness/memory/` provides a JSONL memory store for durable lessons and
governance outcomes.

The memory layer supports:

- category/tag filtering;
- latest-memory lookup;
- text search;
- corrupted-line tolerance;
- persistence across fresh store instances.

## Git Persistence

`harness/core/git/` enforces the repository publication lifecycle.

Capabilities:

- repository inspection;
- uncommitted/untracked/sensitive file detection;
- commit creation;
- branch/remote mismatch detection;
- publication-required status when no remote exists;
- safe publication preparation with real conflict reporting.

## Execution Flow

```text
1. Build a graph with GraphBuilder.
2. Execute with GraphRuntime.
3. Runtime creates or retrieves TaskState.
4. For each node:
   a. emit node-start event;
   b. execute node logic;
   c. store outputs;
   d. checkpoint state;
   e. emit node-complete or node-failed event;
   f. route to next node.
5. Runtime marks task completed, failed, or cancelled.
6. Git persistence verifies commit/publication status when a task changes code.
```

## Current Verification Commands

```bash
python -m harness.tests.run_all_tests
python -m harness.tests.test_website_intelligence
python -m harness.tests.test_redesign_intelligence
python -m harness.tests.test_git_persistence
python -m harness.tests.test_color_intelligence
python -m harness.tests.test_governance
python -m harness.tests.test_seo_analysis
python -m harness.tests.test_client_proposal
python -m harness.tests.test_prospecting
python -m harness.tests.test_runtime_fixes
python -m harness.tests.test_memory
python -m harness.tests.test_checkpoint_persistence
python -m harness.tests.test_agent_cycle
python -m harness.tests.test_design_agent_cycle_node
python -m harness.tests.test_design_judgment
python -m harness.tests.test_design_pipeline_integration
```

## Current Status

The core harness, deterministic design pipeline, governance gate, memory store,
git persistence layer, agent cycle, graph-node integration, and provider-agnostic
design judgment base all have automated coverage.

## Known Remaining Gaps

- Real `QwenAgentProvider.connect()` and `generate()` still need a concrete API
  client and credentials.
- Prospecting, external-reference learning, client-facing proposal generation,
  and outbound delivery are not implemented yet.
- SEO analysis is deterministic/local. It does not yet fetch live SERP,
  Lighthouse, schema.org, or crawler data.

## Version

Harness current architecture snapshot - 2026-08-13.
