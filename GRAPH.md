# Graph Documentation - Harness V0.1

## Overview

This document describes the graph system used in the harness for defining and executing workflows.

## Graph Structure

A graph is a directed graph consisting of:

- **Nodes**: Executable units with unique IDs
- **Edges**: Directed connections between nodes
- **START Node**: Entry point for execution
- **END Node**: Exit point for execution

## Node Types

```python
class NodeType(Enum):
    START = "start"        # Entry point
    END = "end"            # Exit point
    STANDARD = "standard"  # Regular execution node
    CONDITIONAL = "conditional"  # Branching logic (future)
    LOOP = "loop"          # Loop control (future)
```

## Creating Graphs

### Using GraphBuilder (Recommended)

```python
from harness.core.graph import GraphBuilder

graph = GraphBuilder("my_graph") \
    .add_start() \
    .add_node("NODE_A", "Node A", execute_func=my_function) \
    .add_node("NODE_B", "Node B", execute_func=another_function) \
    .add_end() \
    .build()
```

### Manual Construction

```python
from harness.core.graph import Graph, Node, NodeType, Edge

graph = Graph("manual_graph")

# Add nodes
graph.add_node(Node(id="START", name="Start", node_type=NodeType.START))
graph.add_node(Node(id="A", name="Node A", execute_func=my_function))
graph.add_node(Node(id="END", name="End", node_type=NodeType.END))

# Add edges
graph.add_edge(Edge(source="START", target="A"))
graph.add_edge(Edge(source="A", target="END"))
```

## Test Graph

The required test graph for V0.1:

```
START
  ↓
HELLO_NODE
  ↓
QWEN_TEST_NODE
  ↓
TOOL_TEST_NODE
  ↓
END
```

Construction:
```python
from harness.core.graph import GraphBuilder
from harness.nodes import hello_node, qwen_test_node, tool_test_node

graph = GraphBuilder("test_graph") \
    .add_start() \
    .add_node(hello_node()) \
    .add_node(qwen_test_node()) \
    .add_node(tool_test_node()) \
    .add_end() \
    .build()
```

## Execution

```python
from harness.core.runtime import execute_graph

result = execute_graph(graph, "task_001")

print(f"Success: {result.success}")
print(f"Nodes executed: {result.nodes_executed}")
```

## Graph Validation

The `validate()` method checks:

1. Graph has a START node
2. Graph has an END node
3. All nodes are reachable from START
4. All nodes can reach END

```python
is_valid, errors = graph.validate()
if not is_valid:
    print(f"Validation errors: {errors}")
```

## Execution Order

The `get_execution_order()` method returns nodes in topological order:

```python
order = graph.get_execution_order()
# Example: ["START", "A", "B", "C", "END"]
```

## Conditional Edges (Future)

Conditional edges allow branching:

```python
# Edge with condition
graph.add_edge(Edge(
    source="DECISION_NODE",
    target="PATH_A",
    condition="use_path_a"
))
```

## Loops (Future)

Loop support will allow cycles in the graph:

```python
# Create cycle
graph.add_edge(Edge(source="LOOP_END", target="LOOP_START"))
```

## Best Practices

1. **Always use GraphBuilder** for cleaner code
2. **Validate graphs** before execution
3. **Use meaningful node IDs** for debugging
4. **Keep graphs focused** - one responsibility per graph
5. **Test with mock nodes** before production

## Graph Examples

### Simple Sequential Graph

```python
graph = GraphBuilder("sequential") \
    .add_start() \
    .add_node("STEP1", "First Step", execute_func=step1) \
    .add_node("STEP2", "Second Step", execute_func=step2) \
    .add_node("STEP3", "Third Step", execute_func=step3) \
    .add_end() \
    .build()
```

### Parallel-like Pattern (Converging)

```python
graph = GraphBuilder("converge") \
    .add_start() \
    .add_node("SPLIT", "Split", execute_func=split) \
    .add_node("PATH_A", "Path A", execute_func=path_a) \
    .add_node("PATH_B", "Path B", execute_func=path_b) \
    .add_node("MERGE", "Merge", execute_func=merge) \
    .add_end() \
    .build()

# Manually add parallel edges
graph.add_edge(Edge(source="SPLIT", target="PATH_A"))
graph.add_edge(Edge(source="SPLIT", target="PATH_B"))
graph.add_edge(Edge(source="PATH_A", target="MERGE"))
graph.add_edge(Edge(source="PATH_B", target="MERGE"))
```

## State Flow Through Graph

State is passed through nodes:

```
START → state.inputs = initial_data
  ↓
NODE_A → state.outputs["NODE_A"] = result_a
  ↓
NODE_B → Can read state.outputs["NODE_A"]
  ↓
END → Final state contains all outputs
```

## Error Recovery with Checkpoints

After each successful node, a checkpoint is created:

```
NODE_A (success) → CHECKPOINT_CREATED
  ↓
NODE_B (fails after retries)
  ↓
Restore from checkpoint → NODE_A's state restored
```

## Version

Graph System V0.1
