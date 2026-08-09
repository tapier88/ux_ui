# Architecture Documentation - Harness V0.1

## Overview

This document describes the architecture of the autonomous web design agent harness (V0.1).
The harness is built from scratch with a modular, graph-based execution engine.

## Design Principles

1. **Modularity**: Each component is independent and replaceable
2. **Abstraction**: Core logic is decoupled from specific providers (e.g., Qwen-Agent)
3. **Testability**: All components can be tested in isolation with mocks
4. **Recoverability**: Checkpoints enable recovery from errors
5. **Observability**: Events and structured logging provide full visibility
6. **Persistence**: All tasks must be persisted to Git before completion

## Directory Structure

```
/workspace
├── harness/
│   ├── core/           # Core engine components
│   │   ├── graph/      # Graph definition and builder
│   │   ├── state/      # State management and checkpoints
│   │   ├── runtime/    # Execution engine
│   │   ├── orchestrator/ # Orchestration logic (future)
│   │   ├── events/     # Event system
│   │   └── git/        # Git persistence & publication
│   │
│   ├── agents/         # LLM provider abstractions
│   ├── nodes/          # Node implementations
│   ├── tools/          # Tool registry
│   ├── skills/         # Skill registry
│   ├── memory/         # Memory systems (future)
│   ├── config/         # Configuration (future)
│   ├── logs/           # Log output
│   └── tests/          # Test suite
│
├── projects/           # Project outputs (future)
├── scripts/            # Utility scripts
├── TASK_MANIFEST.json  # Task persistence history
└── docs/               # Documentation
```

## Core Components

### 1. Graph Engine (`harness/core/graph/`)

**Purpose**: Define and validate directed graphs for workflow execution.

**Key Classes**:
- `Graph`: Represents a directed graph with nodes and edges
- `Node`: Represents a node with id, name, type, and execution function
- `Edge`: Represents a connection between nodes
- `NodeType`: Enum for START, END, STANDARD, CONDITIONAL, LOOP
- `GraphBuilder`: Fluent builder for constructing graphs

**Features**:
- Graph validation (reachability, start/end nodes)
- Topological ordering for execution
- Support for conditional edges (future)

### 2. State Engine (`harness/core/state/`)

**Purpose**: Manage shared state across all nodes in a graph execution.

**Key Classes**:
- `TaskState`: Complete state of a task including inputs, outputs, history, errors
- `Checkpoint`: Snapshot of state at a point in time
- `StateManager`: Manages states for all tasks

**Features**:
- Task isolation by task_id
- History tracking
- Error recording
- Checkpoint creation and restoration

### 3. Runtime Engine (`harness/core/runtime/`)

**Purpose**: Execute graphs with error handling, retries, and checkpointing.

**Key Classes**:
- `GraphRuntime`: Main execution engine
- `RuntimeConfig`: Configuration for execution behavior
- `ExecutionResult`: Result of graph execution

**Features**:
- Sequential node execution
- Automatic retry on failure
- Checkpoint creation after each successful node
- Event emission throughout execution
- Graceful error handling

### 4. Event System (`harness/core/events/`)

**Purpose**: Broadcast system events for observability and debugging.

**Event Types**:
- TASK_STARTED / TASK_COMPLETED / TASK_FAILED
- NODE_STARTED / NODE_COMPLETED / NODE_FAILED
- TOOL_STARTED / TOOL_COMPLETED
- CHECKPOINT_CREATED
- ERROR_RECOVERED

**Key Classes**:
- `Event`: Structured event with timestamp, task_id, node_id, status
- `EventEmitter`: Publish-subscribe event broadcaster

### 5. Tool Registry (`harness/tools/`)

**Purpose**: Register, discover, and execute tools.

**Key Classes**:
- `ToolRegistry`: Central registry for tools
- `ToolDefinition`: Tool metadata and function
- `ToolResult`: Execution result with status

**Mock Tools** (for testing):
- `mock_search`: Fake search results
- `mock_browser`: Fake page content
- `mock_file`: Simulated file operations
- `mock_data`: Data processing simulation

### 6. Skill Registry (`harness/skills/`)

**Purpose**: Register and load skills (reusable capabilities).

**Key Classes**:
- `SkillRegistry`: Central registry for skills
- `SkillDefinition`: Skill metadata and function

**Test Skill**:
- `test-skill`: Basic skill for validation

### 7. Qwen Adapter (`harness/agents/`)

**Purpose**: Abstract LLM provider to avoid coupling.

**Key Classes**:
- `LLMProvider`: Abstract base class
- `MockLLMProvider`: Mock implementation for testing
- `QwenAgentProvider`: Real Qwen-Agent implementation (requires credentials)
- `LLMAdapterFactory`: Factory for creating providers

**Connection Guide**:
To connect real Qwen-Agent:
1. Set API key and endpoint in environment
2. Create `QwenAgentProvider` with credentials
3. Call `connect()` to establish connection
4. Use `generate()` for completions

### 8. Node System (`harness/nodes/`)

**Purpose**: Standard interface for executable units.

**Base Interface**:
```python
class BaseNode:
    def __init__(self, node_id: str, name: str, node_type: NodeType)
    def execute(self, state: TaskState) -> Any
```

**Standard Nodes**:
- `HelloNode`: Simple greeting node
- `QwenTestNode`: Tests LLM adapter
- `ToolTestNode`: Tests tool registry
- `SkillTestNode`: Tests skill registry
- `ErrorTestNode`: For testing error handling
- `CheckpointTestNode`: For testing checkpoints
- `DataPassNode`: Passes data through

## Execution Flow

```
1. Create Graph using GraphBuilder
2. Create Runtime with configuration
3. Call runtime.execute(graph, task_id, initial_state)
4. Runtime creates TaskState
5. For each node:
   a. Emit NODE_STARTED
   b. Execute node.execute(state)
   c. Store output in state.outputs
   d. Create checkpoint
   e. Emit NODE_COMPLETED
   f. Get next node from graph
6. Emit TASK_COMPLETED
7. Return ExecutionResult
```

## Error Handling Strategy

1. **Retry**: Failed nodes are retried up to `max_retries` times
2. **Checkpoint**: State is saved after each successful node
3. **Continue**: On permanent failure, execution can continue to END
4. **Recovery**: Task can be restored from last checkpoint

## Testing

Run all tests:
```bash
python -m harness.tests.run_all_tests
```

Test categories:
- Graph tests (creation, validation, execution order)
- State tests (creation, updates, history)
- Checkpoint tests (creation, restoration)
- Event tests (creation, emission, history)
- Tool tests (registry, execution, mocks)
- Skill tests (registry, execution)
- Qwen adapter tests (mock provider, generation)
- Node tests (all standard nodes)
- Runtime tests (execution, error handling)

## HARNESS STATUS

```
HARNESS STATUS
===============
Graph: PASS
State: PASS
Nodes: PASS
Tools: PASS
Skills: PASS
Qwen Adapter: PASS
Checkpoint: PASS
Events: PASS
Error Recovery: PASS
Tests: PASS
```

## Future Extensions (Not in V0.1)

- Browser automation
- Web scraping
- Design analysis
- UX analysis
- Frontend generation
- Autonomous outreach
- CRM integration
- Web deployment

## Version

Harness V0.1 - Base Infrastructure
