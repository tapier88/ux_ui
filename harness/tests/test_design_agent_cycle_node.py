"""
Tests for DesignAgentCycleNode graph integration.
"""
import os
import shutil
import tempfile
import unittest

FIXTURE_SOURCE = os.path.join(
    os.path.dirname(__file__), "fixtures", "sample_project"
)


class DesignAgentCycleNodeTestCase(unittest.TestCase):
    def setUp(self):
        self.work_dir = tempfile.mkdtemp(prefix="agent_cycle_node_")
        shutil.copytree(FIXTURE_SOURCE, self.work_dir, dirs_exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)


class TestDesignAgentCycleNode(DesignAgentCycleNodeTestCase):
    def test_node_execute_returns_agent_cycle_result(self):
        from harness.core.state import TaskState
        from harness.nodes import DesignAgentCycleNode

        state = TaskState(task_id="agent-node-direct")
        state.inputs = {
            "project_path": self.work_dir,
            "url": "https://example.com",
            "execute": False,
        }

        result = DesignAgentCycleNode().execute(state)

        self.assertEqual(result["node"], "DesignAgentCycleNode")
        self.assertEqual(result["task_id"], "agent-node-direct")
        self.assertEqual(result["decision"], "ready_to_execute")
        self.assertEqual(
            [step["phase"] for step in result["trace"]],
            ["PLAN", "EXECUTE", "OBSERVE", "EVALUATE", "DECIDE"],
        )

    def test_node_runs_inside_graph_runtime(self):
        from harness.core.graph import Edge, GraphBuilder, Node, NodeType
        from harness.core.runtime import GraphRuntime
        from harness.nodes import design_agent_cycle_node

        graph = GraphBuilder("agent_cycle_graph").add_start().build()
        agent_node = design_agent_cycle_node(project_path=self.work_dir)
        graph.add_node(agent_node)
        graph.add_node(Node(id="END", name="End", node_type=NodeType.END))
        graph.end_node = "END"
        graph.edges = [
            Edge(source="START", target="DESIGN_AGENT_CYCLE_NODE"),
            Edge(source="DESIGN_AGENT_CYCLE_NODE", target="END"),
        ]
        graph._adjacency = {
            "START": [graph.edges[0]],
            "DESIGN_AGENT_CYCLE_NODE": [graph.edges[1]],
            "END": [],
        }

        runtime = GraphRuntime()
        result = runtime.execute(
            graph,
            "agent-node-graph",
            initial_state={
                "url": "https://example.com",
                "execute": False,
                "max_iterations": 2,
            },
        )

        self.assertTrue(result.success, result.errors)
        self.assertIn("DESIGN_AGENT_CYCLE_NODE", result.nodes_executed)


def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDesignAgentCycleNode))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
