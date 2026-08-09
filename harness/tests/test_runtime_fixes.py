"""
Tests for the FASE 0 critical runtime fixes:
- CRITICAL-005: task completion status bug
- CRITICAL-001: node timeout enforcement
- CRITICAL-006: conditional/branching evaluation
- MED-001: max_steps guard against infinite loops
- Cancellation support

Run with: python -m unittest harness.tests.test_runtime_fixes -v
"""
import time
import unittest

from harness.core.graph import Graph, Node, NodeType, Edge, GraphBuilder
from harness.core.runtime import GraphRuntime, RuntimeConfig, NodeTimeoutError
from harness.core.state import get_state_manager


class TestStatusBugFix(unittest.TestCase):
    """CRITICAL-005: a task with a permanently-failing node must not be
    reported as completed/success."""

    def setUp(self):
        get_state_manager().clear_all()

    def test_failed_node_marks_task_failed(self):
        def always_fails(state):
            raise RuntimeError("boom")

        graph = (
            GraphBuilder("status_bug_test")
            .add_start()
            .add_node("FAIL", "Always fails", execute_func=always_fails)
            .add_end()
            .build()
        )

        config = RuntimeConfig()
        config.max_retries = 1
        runtime = GraphRuntime(config)
        result = runtime.execute(graph, "status_bug_task")

        self.assertFalse(result.success)
        state = get_state_manager().get_state("status_bug_task")
        self.assertEqual(state.status, "failed")

    def test_successful_graph_still_reports_completed(self):
        graph = (
            GraphBuilder("status_ok_test")
            .add_start()
            .add_node("OK", "Succeeds", execute_func=lambda state: {"ok": True})
            .add_end()
            .build()
        )

        runtime = GraphRuntime()
        result = runtime.execute(graph, "status_ok_task")

        self.assertTrue(result.success)
        state = get_state_manager().get_state("status_ok_task")
        self.assertEqual(state.status, "completed")


class TestTimeout(unittest.TestCase):
    """CRITICAL-001: timeout_seconds must actually be enforced."""

    def setUp(self):
        get_state_manager().clear_all()

    def test_slow_node_times_out(self):
        def slow_node(state):
            time.sleep(2)
            return {"done": True}

        graph = (
            GraphBuilder("timeout_test")
            .add_start()
            .add_node("SLOW", "Slow node", execute_func=slow_node)
            .add_end()
            .build()
        )

        config = RuntimeConfig()
        config.timeout_seconds = 1
        config.max_retries = 1
        runtime = GraphRuntime(config)

        start = time.time()
        result = runtime.execute(graph, "timeout_task")
        elapsed = time.time() - start

        self.assertFalse(result.success)
        # Must not have blocked anywhere near the full 2s sleep
        self.assertLess(elapsed, 1.8)

    def test_fast_node_not_affected_by_timeout(self):
        graph = (
            GraphBuilder("no_timeout_test")
            .add_start()
            .add_node("FAST", "Fast node", execute_func=lambda state: {"ok": True})
            .add_end()
            .build()
        )

        config = RuntimeConfig()
        config.timeout_seconds = 5
        runtime = GraphRuntime(config)
        result = runtime.execute(graph, "no_timeout_task")

        self.assertTrue(result.success)


class TestMaxSteps(unittest.TestCase):
    """MED-001: a cyclic/misrouted graph must not loop forever."""

    def setUp(self):
        get_state_manager().clear_all()

    def test_infinite_loop_is_capped_by_max_steps(self):
        # Build a graph with a manual cycle: A -> A (bypassing validate())
        graph = Graph("loop_test")
        graph.add_node(Node(id="START", name="Start", node_type=NodeType.START))
        graph.add_node(Node(id="A", name="A", node_type=NodeType.LOOP,
                             execute_func=lambda state: {"tick": True}))
        graph.add_node(Node(id="END", name="End", node_type=NodeType.END))
        graph.add_edge(Edge(source="START", target="A"))
        graph.add_edge(Edge(source="A", target="A"))  # self-loop, taken first
        graph.add_edge(Edge(source="A", target="END"))  # exists so validate() passes,
        # but is never reached because get_next_nodes() returns edges in
        # insertion order and the runtime always follows the first one —
        # this is exactly the kind of routing bug max_steps must catch.

        config = RuntimeConfig()
        config.max_steps = 25
        runtime = GraphRuntime(config)
        result = runtime.execute(graph, "loop_task")

        self.assertFalse(result.success)
        self.assertLessEqual(len(result.nodes_executed), config.max_steps + 2)
        self.assertTrue(
            any(e.get("type") == "max_steps_exceeded" for e in result.errors)
        )


class TestCancellation(unittest.TestCase):
    """Cancellation must stop execution before further nodes run."""

    def setUp(self):
        get_state_manager().clear_all()

    def test_cancel_before_execution_stops_task(self):
        graph = (
            GraphBuilder("cancel_test")
            .add_start()
            .add_node("A", "A", execute_func=lambda state: {"ok": True})
            .add_node("B", "B", execute_func=lambda state: {"ok": True})
            .add_end()
            .build()
        )

        runtime = GraphRuntime()
        runtime.cancel("cancel_task")  # cancel before it even starts
        result = runtime.execute(graph, "cancel_task")

        self.assertFalse(result.success)
        state = get_state_manager().get_state("cancel_task")
        self.assertEqual(state.status, "cancelled")
        self.assertEqual(result.nodes_executed, [])


class TestConditionalBranching(unittest.TestCase):
    """CRITICAL-006: conditional nodes must route based on their
    condition_func's return value, matched against edge labels."""

    def setUp(self):
        get_state_manager().clear_all()

    def test_conditional_routes_to_matching_branch(self):
        graph = Graph("branch_test")
        graph.add_node(Node(id="START", name="Start", node_type=NodeType.START))
        graph.add_node(Node(
            id="CHECK", name="Check", node_type=NodeType.CONDITIONAL,
            condition_func=lambda state: "high" if state.inputs.get("score", 0) > 5 else "low"
        ))
        graph.add_node(Node(id="HIGH", name="High branch",
                             execute_func=lambda state: {"branch": "high"}))
        graph.add_node(Node(id="LOW", name="Low branch",
                             execute_func=lambda state: {"branch": "low"}))
        graph.add_node(Node(id="END", name="End", node_type=NodeType.END))

        graph.add_edge(Edge(source="START", target="CHECK"))
        graph.add_edge(Edge(source="CHECK", target="HIGH", condition="high"))
        graph.add_edge(Edge(source="CHECK", target="LOW", condition="low"))
        graph.add_edge(Edge(source="HIGH", target="END"))
        graph.add_edge(Edge(source="LOW", target="END"))

        runtime = GraphRuntime()
        result = runtime.execute(graph, "branch_high_task", initial_state={"score": 10})
        self.assertIn("HIGH", result.nodes_executed)
        self.assertNotIn("LOW", result.nodes_executed)

        result2 = runtime.execute(graph, "branch_low_task", initial_state={"score": 1})
        self.assertIn("LOW", result2.nodes_executed)
        self.assertNotIn("HIGH", result2.nodes_executed)


class TestCycleDetection(unittest.TestCase):
    """Graph.validate() should flag unintended cycles among STANDARD nodes."""

    def test_validate_rejects_standard_node_cycle(self):
        graph = Graph("bad_cycle")
        graph.add_node(Node(id="START", name="Start", node_type=NodeType.START))
        graph.add_node(Node(id="A", name="A"))
        graph.add_node(Node(id="B", name="B"))
        graph.add_node(Node(id="END", name="End", node_type=NodeType.END))
        graph.add_edge(Edge(source="START", target="A"))
        graph.add_edge(Edge(source="A", target="B"))
        graph.add_edge(Edge(source="B", target="A"))  # cycle
        graph.add_edge(Edge(source="B", target="END"))

        is_valid, errors = graph.validate()
        self.assertFalse(is_valid)
        self.assertTrue(any("Cycle detected" in e for e in errors))

    def test_validate_allows_loop_typed_cycle(self):
        graph = Graph("intentional_loop")
        graph.add_node(Node(id="START", name="Start", node_type=NodeType.START))
        graph.add_node(Node(id="A", name="A", node_type=NodeType.LOOP))
        graph.add_node(Node(id="END", name="End", node_type=NodeType.END))
        graph.add_edge(Edge(source="START", target="A"))
        graph.add_edge(Edge(source="A", target="A"))
        graph.add_edge(Edge(source="A", target="END"))

        is_valid, errors = graph.validate()
        self.assertTrue(is_valid, msg=f"Unexpected errors: {errors}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
