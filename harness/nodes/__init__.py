"""
Nodes - Standard node implementations
"""
from typing import Any, Optional, Callable
from harness.core.graph import Node, NodeType
from harness.core.state import TaskState


class BaseNode(Node):
    """Base class for all nodes"""
    
    def __init__(self, node_id: str, name: str, 
                 node_type: NodeType = NodeType.STANDARD):
        super().__init__(
            id=node_id,
            name=name,
            node_type=node_type
        )
    
    def execute(self, state: TaskState) -> Any:
        """Execute the node - override in subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")


class HelloNode(BaseNode):
    """Simple hello node for testing"""
    
    def __init__(self):
        super().__init__("HELLO_NODE", "Hello Node")
    
    def execute(self, state: TaskState) -> dict:
        """Say hello and return greeting"""
        greeting = "Hello from HelloNode!"
        task_id = state.task_id
        
        result = {
            "greeting": greeting,
            "task_id": task_id,
            "message": f"Processing task {task_id}"
        }
        
        return result


class QwenTestNode(BaseNode):
    """Test node for Qwen adapter"""
    
    def __init__(self):
        super().__init__("QWEN_TEST_NODE", "Qwen Test Node")
    
    def execute(self, state: TaskState) -> dict:
        """Test Qwen adapter functionality"""
        from harness.agents import get_default_provider, LLMRequest
        
        # Use mock provider for testing
        provider = get_default_provider()
        
        # Create request object properly
        from harness.agents import LLMRequest
        request = LLMRequest(prompt="Test prompt from QwenTestNode")
        response = provider.generate(request)
        
        result = {
            "node": "QwenTestNode",
            "prompt": "Test prompt from QwenTestNode",
            "response": response.content,
            "provider_status": provider.get_status().value
        }
        
        return result


class ToolTestNode(BaseNode):
    """Test node for tool registry"""
    
    def __init__(self):
        super().__init__("TOOL_TEST_NODE", "Tool Test Node")
    
    def execute(self, state: TaskState) -> dict:
        """Test tool registry functionality"""
        from harness.tools import get_tool_registry, register_mock_tools
        
        # Register mock tools if not already registered
        register_mock_tools()
        
        registry = get_tool_registry()
        
        # Execute a mock tool
        tool_result = registry.execute_tool("mock_search", query="test query")
        
        result = {
            "node": "ToolTestNode",
            "tools_available": registry.list_tools(),
            "tool_execution": tool_result.to_dict()
        }
        
        return result


class SkillTestNode(BaseNode):
    """Test node for skill registry"""
    
    def __init__(self):
        super().__init__("SKILL_TEST_NODE", "Skill Test Node")
    
    def execute(self, state: TaskState) -> dict:
        """Test skill registry functionality"""
        from harness.skills import get_skill_registry, register_test_skill
        
        # Register test skill if not already registered
        register_test_skill()
        
        registry = get_skill_registry()
        
        # Execute test skill
        skill_result = registry.execute_skill("test-skill", data={"test": "data"})
        
        result = {
            "node": "SkillTestNode",
            "skills_available": registry.list_skills(),
            "skill_execution": skill_result
        }
        
        return result


class ErrorTestNode(BaseNode):
    """Node that throws an error for testing error handling"""
    
    def __init__(self, fail_on_first: bool = True):
        super().__init__("ERROR_TEST_NODE", "Error Test Node")
        self.fail_on_first = fail_on_first
        self.call_count = 0
    
    def execute(self, state: TaskState) -> dict:
        """Throw an error for testing"""
        self.call_count += 1
        
        if self.fail_on_first:
            raise RuntimeError("Intentional error for testing")
        
        return {"error_node": "did not fail this time"}


class CheckpointTestNode(BaseNode):
    """Node for testing checkpoint functionality"""
    
    def __init__(self):
        super().__init__("CHECKPOINT_TEST_NODE", "Checkpoint Test Node")
        self.data_to_save = {}
    
    def execute(self, state: TaskState) -> dict:
        """Save some data to state for checkpoint testing"""
        self.data_to_save = {
            "checkpoint_data": "This should be preserved",
            "counter": len(state.history)
        }
        
        return self.data_to_save


class DataPassNode(BaseNode):
    """Node that passes data through"""
    
    def __init__(self, key: str = "passed_data", value: Any = None):
        super().__init__(f"DATA_PASS_{key.upper()}", f"Data Pass Node ({key})")
        self.key = key
        self.value = value
    
    def execute(self, state: TaskState) -> dict:
        """Pass data through or use input from state"""
        value = self.value
        if value is None and self.key in state.inputs:
            value = state.inputs[self.key]
        
        result = {
            self.key: value,
            "from_node": self.id
        }
        
        return result


def create_node_factory():
    """Factory for creating standard nodes"""
    from harness.nodes.design_agent_cycle_node import design_agent_cycle_node
    
    factories = {
        "hello": lambda: HelloNode(),
        "qwen_test": lambda: QwenTestNode(),
        "tool_test": lambda: ToolTestNode(),
        "skill_test": lambda: SkillTestNode(),
        "error_test": lambda: ErrorTestNode(),
        "checkpoint_test": lambda: CheckpointTestNode(),
        "data_pass": lambda key, value=None: DataPassNode(key, value),
        "design_agent_cycle": lambda project_path=".": design_agent_cycle_node(project_path),
    }
    
    return factories


# Convenience functions
def hello_node() -> Node:
    """Create a HelloNode"""
    node = HelloNode()
    node.execute_func = lambda state: node.execute(state)
    return node


def qwen_test_node() -> Node:
    """Create a QwenTestNode"""
    node = QwenTestNode()
    node.execute_func = lambda state: node.execute(state)
    return node


def tool_test_node() -> Node:
    """Create a ToolTestNode"""
    node = ToolTestNode()
    node.execute_func = lambda state: node.execute(state)
    return node


def skill_test_node() -> Node:
    """Create a SkillTestNode"""
    node = SkillTestNode()
    node.execute_func = lambda state: node.execute(state)
    return node


def error_test_node(fail_on_first: bool = True) -> Node:
    """Create an ErrorTestNode"""
    node = ErrorTestNode(fail_on_first)
    node.execute_func = lambda state: node.execute(state)
    return node


from harness.nodes.design_agent_cycle_node import (  # noqa: E402
    DesignAgentCycleNode,
    design_agent_cycle_node,
)
