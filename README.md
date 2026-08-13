# Web Design Autonomous Agent - Harness V0.1

## Overview

This is the base harness infrastructure for our autonomous web design agent.
Built from scratch with a modular, graph-based execution engine.

## Architecture

```
/workspace
├── harness/
│   ├── core/
│   │   ├── graph/        # Graph engine (nodes, edges, execution)
│   │   ├── state/        # Shared state management
│   │   ├── runtime/      # Runtime execution engine
│   │   ├── orchestrator/ # Orchestration logic
│   │   ├── events/       # Event system
│   │   └── git/          # Git persistence & publication
│   │
│   ├── agents/           # Agent definitions
│   ├── nodes/            # Node implementations
│   ├── tools/            # Tool registry and implementations
│   ├── skills/           # Skill registry and implementations
│   ├── memory/           # Memory systems
│   ├── config/           # Configuration
│   ├── logs/             # Log files
│   └── tests/            # Test suite
│
├── projects/             # Project outputs
├── scripts/              # Utility scripts
├── .env.example          # Environment variables template
├── TASK_MANIFEST.json    # Task persistence history
├── README.md             # This file
├── ARCHITECTURE.md       # Detailed architecture
└── GRAPH.md              # Graph documentation
```

## Core Components

### 1. Graph Engine
- Supports nodes, edges, START, END
- Sequential execution, branching, conditions, loops
- Error recovery

### 2. State Engine
- Shared state across all nodes
- Task ID, metadata, inputs, outputs, history, errors, checkpoints
- Git persistence fields: commit_sha, branch, remote, publication_status, remote_verified

### 3. Node System
- Standard interface: id, name, execute(), input, output, error handling

### 4. Tool System
- Tool Registry with register, get, list, execute capabilities
- Mock tools for testing

### 5. Skill System
- Skill Registry with register, load, list capabilities

### 6. Qwen Adapter
- Abstract LLM provider layer
- Mock implementation for testing

### 7. Checkpoint System
- Save state after each successful node
- Restore from last valid checkpoint
- Includes Git state for recovery

### 8. Event System
- TASK_STARTED, NODE_STARTED, NODE_COMPLETED, NODE_FAILED
- TOOL_STARTED, TOOL_COMPLETED, CHECKPOINT_CREATED, TASK_COMPLETED
- GIT_STATUS_CHECKED, COMMIT_CREATED, PUBLICATION_REQUIRED
- PUBLICATION_STARTED, PUBLICATION_COMPLETED, REMOTE_COMMIT_VERIFIED
- TASK_PERSISTENCE_FAILED

### 9. Logging
- Structured logging for execution reconstruction

### 10. Error Handling
- Retry mechanism, error state, checkpoint recovery

### 11. Git Persistence (NEW - V0.1)
- **GitInspector**: Repository state inspection
- **GitPersistence**: Commit creation and management
- **GitPublicationProvider**: Remote publication abstraction
- **GitValidator**: Validation gates for commits and publication
- **TaskManifest**: Task persistence history and recovery

### 12. Design Pipeline Governance
- **DesignPipelineNode**: Runs website intelligence, redesign intelligence,
  resource selection, execution planning, governance, and site building in order.
- **GovernanceGate**: Blocks real `site_builder` writes when deterministic
  quality signals fail the configured threshold.
- **Auditable signals**: brand alignment, accessibility, visual craft,
  performance, SEO impact, and originality are derived from concrete pipeline
  outputs and returned in the node result.

### 13. Deterministic Agent Cycle
- **DeterministicDesignAgent**: Wraps `DesignPipelineNode` in an explicit
  `PLAN -> EXECUTE -> OBSERVE -> EVALUATE -> DECIDE` cycle without requiring an
  external LLM provider.
- **Safe default**: `execute=False` performs a dry-run and returns
  `ready_to_execute` only if planning and governance pass.
- **Real build path**: `execute=True` writes files only after the dry-run
  evaluation passes.

## Task Completion Lifecycle

A task can only be marked as **COMPLETE** after passing through these stages:

```
IMPLEMENTING → TESTING → READY_TO_COMMIT → COMMITTED → 
READY_TO_PUBLISH → PUBLISHED → VERIFIED → COMPLETE
```

### Critical Rules:

1. **Tests must pass** before any commit
2. **No sensitive files** (.env, tokens, API keys, passwords, credentials)
3. **Commit must be created** with proper message
4. **Commit must be published** to remote (GitHub)
5. **Remote commit must be verified** on the remote branch

If publication is not possible in the current environment:
- Status becomes: `PUBLICATION_REQUIRED`
- Task status: `INCOMPLETE — GITHUB PUBLICATION REQUIRED`
- Task CANNOT be marked as COMPLETE

## Quick Start

```bash
# Run tests
python -m harness.tests.run_all_tests

# Run test graph
python -m harness.tests.test_graph_execution

# Run Git persistence tests
python harness/tests/test_git_persistence.py
```

On Windows/PowerShell these test runners now configure their own console
output and do not require setting `PYTHONUTF8=1` manually.

For the current end-to-end pipeline guard, run:

```bash
python -m harness.tests.test_design_pipeline_integration
```

For the deterministic agent-cycle guard, run:

```bash
python -m harness.tests.test_agent_cycle
```

## Status

See HARNESS_STATUS section in test output.

## License

MIT
