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
│   │   └── events/       # Event system
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

### 8. Event System
- TASK_STARTED, NODE_STARTED, NODE_COMPLETED, NODE_FAILED
- TOOL_STARTED, TOOL_COMPLETED, CHECKPOINT_CREATED, TASK_COMPLETED

### 9. Logging
- Structured logging for execution reconstruction

### 10. Error Handling
- Retry mechanism, error state, checkpoint recovery

## Quick Start

```bash
# Run tests
python -m harness.tests.run_all_tests

# Run test graph
python -m harness.tests.test_graph_execution
```

## Status

See HARNESS_STATUS section in test output.

## License

MIT