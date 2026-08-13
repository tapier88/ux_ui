"""
DesignAgentCycleNode - graph node wrapper for DeterministicDesignAgent.

This lets the Fase 3 PLAN -> EXECUTE -> OBSERVE -> EVALUATE -> DECIDE cycle
participate in normal harness graphs instead of being callable only as a
standalone Python class.
"""
from typing import TYPE_CHECKING, Optional

from harness.core.graph import NodeType
from harness.core.state import TaskState
from harness.nodes import BaseNode

if TYPE_CHECKING:
    from harness.agents import DeterministicDesignAgent


class DesignAgentCycleNode(BaseNode):
    """
    Runs DeterministicDesignAgent from graph state inputs.

    Expected state.inputs:
        project_path (str): project to inspect/build. Defaults to constructor.
        url (str): optional live URL/context.
        resource_hub_options (dict): optional resource selection overrides.
        execute (bool): if False, dry-run only; if True, allow real build after
            passing dry-run evaluation.
        governance_threshold (float): quality gate threshold.
        max_iterations (int): bounded planning/evaluation attempts.
    """

    def __init__(
        self,
        node_id: str = "DESIGN_AGENT_CYCLE_NODE",
        name: str = "Design Agent Cycle Node",
        project_path: str = ".",
        agent: Optional["DeterministicDesignAgent"] = None,
    ):
        super().__init__(node_id, name, NodeType.STANDARD)
        from harness.agents import DeterministicDesignAgent

        self.project_path = project_path
        self.agent = agent or DeterministicDesignAgent()

    def execute(self, state: TaskState) -> dict:
        result = self.agent.run(
            project_path=state.inputs.get("project_path", self.project_path),
            task_id=state.task_id,
            url=state.inputs.get("url"),
            resource_hub_options=state.inputs.get("resource_hub_options", {}),
            execute=bool(state.inputs.get("execute", False)),
            governance_threshold=state.inputs.get("governance_threshold", 75.0),
            max_iterations=state.inputs.get("max_iterations", 1),
        )

        return {
            "node": "DesignAgentCycleNode",
            **result.to_dict(),
        }


def design_agent_cycle_node(project_path: str = ".") -> DesignAgentCycleNode:
    """Create a DesignAgentCycleNode with execute_func wired for GraphRuntime."""
    node = DesignAgentCycleNode(project_path=project_path)
    node.execute_func = lambda state: node.execute(state)
    return node
