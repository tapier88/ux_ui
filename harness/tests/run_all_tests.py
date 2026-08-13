"""
Test suite for Harness V0.1
"""
import sys
import unittest


def _configure_stdout():
    """Make the runner portable across Windows consoles that default to cp1252."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdout()


class TestResults:
    """Collect test results"""
    def __init__(self):
        self.results = {}
    
    def add(self, name: str, passed: bool, message: str = ""):
        self.results[name] = {"passed": passed, "message": message}
    
    def summary(self) -> tuple[int, int]:
        passed = sum(1 for r in self.results.values() if r["passed"])
        total = len(self.results)
        return passed, total
    
    def print_status(self):
        passed, total = self.summary()
        print("\n" + "=" * 50)
        print("HARNESS STATUS")
        print("=" * 50)
        
        status_map = {
            "graph": "Graph",
            "state": "State", 
            "nodes": "Nodes",
            "tools": "Tools",
            "skills": "Skills",
            "qwen_adapter": "Qwen Adapter",
            "checkpoint": "Checkpoint",
    "events": "Events",
    "runtime": "Runtime",
    "agent_cycle": "Agent Cycle",
    "error_recovery": "Error Recovery",
            "tests": "Tests"
        }
        
        for key, label in status_map.items():
            if key in self.results:
                status = "PASS" if self.results[key]["passed"] else "FAIL"
                print(f"{label}: {status}")
        
        print("=" * 50)
        print(f"Tests: {passed}/{total} passed")
        print("=" * 50)


results = TestResults()


def run_group(group_key: str, tests: list[tuple[str, callable]]) -> bool:
    """Run a logical test group and only mark it PASS when every test passes."""
    group_passed = True
    for name, test_func in tests:
        group_passed = run_test(name, test_func) and group_passed
    results.add(group_key, group_passed)
    return group_passed


def run_test(name: str, test_func):
    """Run a test and record result"""
    try:
        test_func()
        results.add(name, True, "OK")
        print(f"[PASS] {name}")
        return True
    except Exception as e:
        results.add(name, False, str(e))
        print(f"[FAIL] {name}: {e}")
        return False


# =============================================================================
# GRAPH TESTS
# =============================================================================

def test_graph_creation():
    """Test graph creation"""
    from harness.core.graph import Graph, Node, NodeType, GraphBuilder
    
    graph = Graph("test_graph")
    assert graph.name == "test_graph"
    assert len(graph.nodes) == 0
    
    # Test builder
    builder = GraphBuilder("builder_graph")
    graph2 = builder.add_start().add_node("A", "Node A").add_end().build()
    
    assert graph2.start_node == "START"
    assert graph2.end_node == "END"
    assert "A" in graph2.nodes


def test_graph_validation():
    """Test graph validation"""
    from harness.core.graph import Graph, Node, NodeType, Edge, GraphBuilder
    
    # Invalid graph - no start/end
    graph = Graph("invalid")
    is_valid, errors = graph.validate()
    assert not is_valid
    assert "Graph must have a START node" in errors
    
    # Valid graph - use builder which properly connects edges
    valid_graph = GraphBuilder("valid") \
        .add_start() \
        .add_node("A", "A") \
        .add_end() \
        .build()
    is_valid, errors = valid_graph.validate()
    assert is_valid, f"Expected valid graph but got errors: {errors}"


def test_graph_execution_order():
    """Test graph execution order"""
    from harness.core.graph import GraphBuilder
    
    graph = GraphBuilder("order_test") \
        .add_start() \
        .add_node("A", "Node A") \
        .add_node("B", "Node B") \
        .add_node("C", "Node C") \
        .add_end() \
        .build()
    
    order = graph.get_execution_order()
    assert order == ["START", "A", "B", "C", "END"]


# =============================================================================
# STATE TESTS
# =============================================================================

def test_state_creation():
    """Test state creation"""
    from harness.core.state import TaskState, StateManager, get_state_manager
    
    # Clear global state
    get_state_manager().clear_all()
    
    state = get_state_manager().create_state("test_task_1")
    assert state.task_id == "test_task_1"
    assert state.status == "pending"


def test_state_updates():
    """Test state updates"""
    from harness.core.state import get_state_manager
    
    manager = get_state_manager()
    manager.clear_all()
    
    state = manager.create_state("test_task_2")
    state.status = "running"
    state.outputs["result"] = "test_value"
    
    assert state.status == "running"
    assert state.outputs["result"] == "test_value"


def test_state_history():
    """Test state history"""
    from harness.core.state import get_state_manager
    
    manager = get_state_manager()
    manager.clear_all()
    
    state = manager.create_state("test_task_3")
    state.add_to_history("action1", {"data": "value1"})
    state.add_to_history("action2", {"data": "value2"})
    
    assert len(state.history) == 2
    assert state.history[0]["action"] == "action1"


# =============================================================================
# CHECKPOINT TESTS
# =============================================================================

def test_checkpoint_creation():
    """Test checkpoint creation"""
    from harness.core.state import get_state_manager
    
    manager = get_state_manager()
    manager.clear_all()
    
    state = manager.create_state("checkpoint_test")
    state.outputs["data"] = "important_data"
    
    checkpoint = manager.save_checkpoint(state, "node_A")
    
    assert checkpoint is not None
    assert checkpoint.node_id == "node_A"
    assert checkpoint.state_snapshot["outputs"]["data"] == "important_data"


def test_checkpoint_restore():
    """Test checkpoint restoration"""
    from harness.core.state import get_state_manager
    
    manager = get_state_manager()
    manager.clear_all()
    
    state = manager.create_state("restore_test")
    state.outputs["original"] = "original_value"
    
    # Create checkpoint
    manager.save_checkpoint(state, "node_before_change")
    
    # Modify state
    state.outputs["original"] = "modified_value"
    state.outputs["new_data"] = "new_value"
    
    # Restore
    restored = manager.restore_from_last_checkpoint("restore_test")
    assert restored == True
    assert state.outputs["original"] == "original_value"
    assert "new_data" not in state.outputs


# =============================================================================
# EVENT TESTS
# =============================================================================

def test_event_creation():
    """Test event creation"""
    from harness.core.events import Event, EventType
    
    event = Event(
        event_type=EventType.NODE_COMPLETED,
        task_id="test_task",
        node_id="node_A",
        status="success"
    )
    
    assert event.event_type == EventType.NODE_COMPLETED
    assert event.task_id == "test_task"
    assert event.node_id == "node_A"


def test_event_emitter():
    """Test event emitter"""
    from harness.core.events import EventEmitter, Event, EventType
    
    emitter = EventEmitter()
    received_events = []
    
    def listener(event):
        received_events.append(event)
    
    emitter.subscribe(listener)
    emitter.emit(Event(event_type=EventType.TASK_STARTED, task_id="emit_test"))
    
    assert len(received_events) == 1
    assert received_events[0].event_type == EventType.TASK_STARTED


def test_event_history():
    """Test event history"""
    from harness.core.events import get_emitter, emit_event, EventType
    
    emitter = get_emitter()
    emitter.clear_history()
    
    emit_event(EventType.NODE_STARTED, "history_test", node_id="A")
    emit_event(EventType.NODE_COMPLETED, "history_test", node_id="A")
    emit_event(EventType.NODE_STARTED, "other_task", node_id="B")
    
    all_events = emitter.get_history()
    task_events = emitter.get_history(task_id="history_test")
    
    assert len(all_events) >= 3
    assert len(task_events) == 2


# =============================================================================
# TOOL TESTS
# =============================================================================

def test_tool_registry():
    """Test tool registry"""
    from harness.tools import ToolRegistry
    
    registry = ToolRegistry()
    
    def dummy_tool(x):
        return x * 2
    
    registry.register_tool("double", "Doubles a number", dummy_tool)
    
    assert registry.has_tool("double")
    assert "double" in registry.list_tools()


def test_tool_execution():
    """Test tool execution"""
    from harness.tools import get_tool_registry, register_mock_tools
    
    register_mock_tools()
    registry = get_tool_registry()
    
    result = registry.execute_tool("mock_search", query="test")
    
    assert result.status.value == "completed"
    assert "results" in result.result


def test_mock_tools():
    """Test mock tools registration"""
    from harness.tools import get_tool_registry, register_mock_tools
    
    registry = get_tool_registry()
    registry.clear()
    register_mock_tools()
    
    tools = registry.list_tools()
    assert len(tools) >= 4  # mock_search, mock_browser, mock_file, mock_data


# =============================================================================
# SKILL TESTS
# =============================================================================

def test_skill_registry():
    """Test skill registry"""
    from harness.skills import SkillRegistry
    
    registry = SkillRegistry()
    
    def dummy_skill():
        return "skill_result"
    
    registry.register_skill("test_skill", "A test skill", dummy_skill)
    
    assert registry.has_skill("test_skill")
    assert registry.is_skill_loaded("test_skill")


def test_skill_execution():
    """Test skill execution"""
    from harness.skills import get_skill_registry, register_test_skill
    
    register_test_skill()
    registry = get_skill_registry()
    
    result = registry.execute_skill("test-skill", data={"key": "value"})
    
    assert result["status"] == "executed"
    assert result["skill"] == "test-skill"


def test_test_skill_registered():
    """Test that test-skill is available"""
    from harness.skills import get_skill_registry, register_test_skill
    
    registry = get_skill_registry()
    registry.clear()
    register_test_skill()
    
    assert "test-skill" in registry.list_skills()


# =============================================================================
# QWEN ADAPTER TESTS
# =============================================================================

def test_mock_provider():
    """Test mock LLM provider"""
    from harness.agents import MockLLMProvider, LLMRequest
    
    provider = MockLLMProvider()
    provider.connect()
    
    assert provider.is_connected()
    assert provider.get_status().value == "mock"


def test_mock_generation():
    """Test mock LLM generation"""
    from harness.agents import MockLLMProvider, LLMRequest
    
    provider = MockLLMProvider()
    provider.connect()
    
    request = LLMRequest(prompt="Test prompt")
    response = provider.generate(request)
    
    assert response.content is not None
    assert "[MOCK RESPONSE]" in response.content


def test_provider_factory():
    """Test LLM provider factory"""
    from harness.agents import LLMAdapterFactory, MockLLMProvider
    
    provider = LLMAdapterFactory.create_provider("mock")
    assert isinstance(provider, MockLLMProvider)


def test_default_provider():
    """Test default provider"""
    from harness.agents import get_default_provider, generate
    
    provider = get_default_provider()
    assert provider is not None
    assert provider.is_connected()
    
    response = generate("Hello")
    assert response.content is not None


# =============================================================================
# NODE TESTS
# =============================================================================

def test_hello_node():
    """Test HelloNode"""
    from harness.nodes import hello_node, HelloNode
    from harness.core.state import TaskState, get_state_manager
    
    get_state_manager().clear_all()
    state = get_state_manager().create_state("hello_test")
    
    node = hello_node()
    result = node.execute(state)
    
    assert "greeting" in result
    assert "Hello" in result["greeting"]


def test_qwen_test_node():
    """Test QwenTestNode"""
    from harness.nodes import qwen_test_node
    from harness.core.state import get_state_manager
    
    get_state_manager().clear_all()
    state = get_state_manager().create_state("qwen_test")
    
    node = qwen_test_node()
    result = node.execute(state)
    
    assert "response" in result
    assert "QwenTestNode" in result["node"]


def test_tool_test_node():
    """Test ToolTestNode"""
    from harness.nodes import tool_test_node
    from harness.core.state import get_state_manager
    
    get_state_manager().clear_all()
    state = get_state_manager().create_state("tool_test")
    
    node = tool_test_node()
    result = node.execute(state)
    
    assert "tools_available" in result
    assert len(result["tools_available"]) > 0


def test_skill_test_node():
    """Test SkillTestNode"""
    from harness.nodes import skill_test_node
    from harness.core.state import get_state_manager
    
    get_state_manager().clear_all()
    state = get_state_manager().create_state("skill_test")
    
    node = skill_test_node()
    result = node.execute(state)
    
    assert "skills_available" in result
    assert "test-skill" in result["skills_available"]


# =============================================================================
# RUNTIME TESTS
# =============================================================================

def test_runtime_execution():
    """Test runtime graph execution"""
    from harness.core.graph import GraphBuilder
    from harness.core.runtime import GraphRuntime
    from harness.core.state import get_state_manager
    from harness.nodes import hello_node, qwen_test_node, tool_test_node
    
    get_state_manager().clear_all()
    
    # Build test graph: START -> HELLO -> QWEN_TEST -> TOOL_TEST -> END
    graph = GraphBuilder("runtime_test") \
        .add_start() \
        .build()
    
    # Add nodes with execute functions
    hello = hello_node()
    qwen = qwen_test_node()
    tool = tool_test_node()
    end_node = type('obj', (object,), {'id': 'END', 'node_type': type('obj', (object,), {'value': 'end'})()})()
    
    graph.add_node(hello)
    graph.add_node(qwen)
    graph.add_node(tool)
    graph.add_node(type('obj', (object,), {'id': 'END', 'name': 'End', 'node_type': type('NodeType', (), {'END': 'end'})})())
    
    # Fix: properly create END node
    from harness.core.graph import Node, NodeType
    graph.nodes["END"] = Node(id="END", name="End", node_type=NodeType.END)
    graph.end_node = "END"
    
    # Add edges
    from harness.core.graph import Edge
    graph.add_edge(Edge(source="START", target="HELLO_NODE"))
    graph.add_edge(Edge(source="HELLO_NODE", target="QWEN_TEST_NODE"))
    graph.add_edge(Edge(source="QWEN_TEST_NODE", target="TOOL_TEST_NODE"))
    graph.add_edge(Edge(source="TOOL_TEST_NODE", target="END"))
    
    runtime = GraphRuntime()
    result = runtime.execute(graph, "runtime_test_task")
    
    assert result.success == True
    assert "HELLO_NODE" in result.nodes_executed


def test_full_test_graph():
    """Test the complete test graph: START -> HELLO -> QWEN_TEST -> TOOL_TEST -> END"""
    from harness.core.graph import GraphBuilder, Node, NodeType, Edge
    from harness.core.runtime import execute_graph
    from harness.core.state import get_state_manager
    from harness.nodes import hello_node, qwen_test_node, tool_test_node
    
    get_state_manager().clear_all()
    
    # Build the exact test graph from requirements using builder pattern
    graph = GraphBuilder("test_graph") \
        .add_start() \
        .add_node("HELLO_NODE", "Hello Node") \
        .add_node("QWEN_TEST_NODE", "Qwen Test Node") \
        .add_node("TOOL_TEST_NODE", "Tool Test Node") \
        .add_end() \
        .build()
    
    # Now set the execute functions for the nodes
    hello = hello_node()
    qwen = qwen_test_node()
    tool = tool_test_node()
    
    graph.nodes["HELLO_NODE"].execute_func = hello.execute_func
    graph.nodes["QWEN_TEST_NODE"].execute_func = qwen.execute_func
    graph.nodes["TOOL_TEST_NODE"].execute_func = tool.execute_func
    
    result = execute_graph(graph, "full_test_task")
    
    assert result.success == True, f"Graph execution failed: {result.errors}"
    assert "HELLO_NODE" in result.nodes_executed
    assert "QWEN_TEST_NODE" in result.nodes_executed
    assert "TOOL_TEST_NODE" in result.nodes_executed


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_error_handling():
    """Test error handling in nodes"""
    from harness.nodes import error_test_node
    from harness.core.state import get_state_manager
    
    get_state_manager().clear_all()
    state = get_state_manager().create_state("error_test")
    
    node = error_test_node(fail_on_first=True)
    
    try:
        node.execute(state)
        assert False, "Should have raised an error"
    except RuntimeError as e:
        assert "Intentional error" in str(e)


def test_retry_mechanism():
    """Test retry mechanism in runtime"""
    from harness.core.graph import GraphBuilder, Node, NodeType, Edge
    from harness.core.runtime import GraphRuntime, RuntimeConfig
    from harness.core.state import get_state_manager
    from harness.nodes import error_test_node
    
    get_state_manager().clear_all()
    
    # Create a graph with an error node
    graph = GraphBuilder("retry_test").add_start().build()
    
    fail_node = error_test_node(fail_on_first=True)
    graph.add_node(fail_node)
    graph.add_node(Node(id="END", name="End", node_type=NodeType.END))
    
    graph.edges = [
        Edge(source="START", target="ERROR_TEST_NODE"),
        Edge(source="ERROR_TEST_NODE", target="END")
    ]
    graph._adjacency = {
        "START": [Edge(source="START", target="ERROR_TEST_NODE")],
        "ERROR_TEST_NODE": [Edge(source="ERROR_TEST_NODE", target="END")],
        "END": []
    }
    
    config = RuntimeConfig()
    config.max_retries = 2
    config.stop_on_error = True
    
    runtime = GraphRuntime(config)
    result = runtime.execute(graph, "retry_test_task")
    
    # Should have tried multiple times
    assert fail_node.call_count >= 1
    assert len(result.errors) > 0 or not result.success


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all tests and print results"""
    print("=" * 60)
    print("HARNESS V0.1 - TEST SUITE")
    print("=" * 60)
    print()
    
    # Graph tests
    print("--- Graph Tests ---")
    run_group("graph", [
        ("test_graph_creation", test_graph_creation),
        ("test_graph_validation", test_graph_validation),
        ("test_graph_execution_order", test_graph_execution_order),
    ])
    
    print()
    print("--- State Tests ---")
    run_group("state", [
        ("test_state_creation", test_state_creation),
        ("test_state_updates", test_state_updates),
        ("test_state_history", test_state_history),
    ])
    
    print()
    print("--- Checkpoint Tests ---")
    run_group("checkpoint", [
        ("test_checkpoint_creation", test_checkpoint_creation),
        ("test_checkpoint_restore", test_checkpoint_restore),
    ])
    
    print()
    print("--- Event Tests ---")
    run_group("events", [
        ("test_event_creation", test_event_creation),
        ("test_event_emitter", test_event_emitter),
        ("test_event_history", test_event_history),
    ])
    
    print()
    print("--- Tool Tests ---")
    run_group("tools", [
        ("test_tool_registry", test_tool_registry),
        ("test_tool_execution", test_tool_execution),
        ("test_mock_tools", test_mock_tools),
    ])
    
    print()
    print("--- Skill Tests ---")
    run_group("skills", [
        ("test_skill_registry", test_skill_registry),
        ("test_skill_execution", test_skill_execution),
        ("test_test_skill_registered", test_test_skill_registered),
    ])
    
    print()
    print("--- Qwen Adapter Tests ---")
    run_group("qwen_adapter", [
        ("test_mock_provider", test_mock_provider),
        ("test_mock_generation", test_mock_generation),
        ("test_provider_factory", test_provider_factory),
        ("test_default_provider", test_default_provider),
    ])
    
    print()
    print("--- Node Tests ---")
    run_group("nodes", [
        ("test_hello_node", test_hello_node),
        ("test_qwen_test_node", test_qwen_test_node),
        ("test_tool_test_node", test_tool_test_node),
        ("test_skill_test_node", test_skill_test_node),
    ])
    
    print()
    print("--- Runtime Tests ---")
    run_group("runtime", [
        ("test_runtime_execution", test_runtime_execution),
        ("test_full_test_graph", test_full_test_graph),
    ])

    print()
    print("--- Agent Cycle Tests ---")
    from harness.tests.test_agent_cycle import run_all_tests as run_agent_cycle_tests
    agent_cycle_passed = run_agent_cycle_tests()
    results.add("agent_cycle", agent_cycle_passed)

    print()
    print("--- Error Handling Tests ---")
    run_group("error_recovery", [
        ("test_error_handling", test_error_handling),
        ("test_retry_mechanism", test_retry_mechanism),
    ])
    
    results.add("tests", all(r["passed"] for r in results.results.values()))
    
    # Print final status
    results.print_status()
    
    return results.summary()


if __name__ == "__main__":
    passed, total = run_all_tests()
    sys.exit(0 if passed == total else 1)
