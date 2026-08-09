"""
Tool Registry - Tool registration and execution system
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
from enum import Enum


class ToolStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ToolDefinition:
    """Definition of a tool"""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "metadata": self.metadata
        }


@dataclass
class ToolResult:
    """Result of a tool execution"""
    tool_name: str
    status: ToolStatus
    result: Any = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "result": self.result,
            "error": self.error
        }


class ToolRegistry:
    """Registry for tools"""
    
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
    
    def register_tool(self, name: str, description: str, 
                     func: Callable, parameters: Optional[Dict[str, Any]] = None,
                     **metadata) -> ToolDefinition:
        """Register a new tool"""
        tool = ToolDefinition(
            name=name,
            description=description,
            func=func,
            parameters=parameters or {},
            metadata=metadata
        )
        self._tools[name] = tool
        return tool
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def execute_tool(self, name: str, *args, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self._tools.get(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                status=ToolStatus.FAILED,
                error=f"Tool '{name}' not found"
            )
        
        try:
            result = tool.func(*args, **kwargs)
            return ToolResult(
                tool_name=name,
                status=ToolStatus.COMPLETED,
                result=result
            )
        except Exception as e:
            return ToolResult(
                tool_name=name,
                status=ToolStatus.FAILED,
                error=str(e)
            )
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool exists"""
        return name in self._tools
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]
            return True
        return False
    
    def clear(self):
        """Clear all tools"""
        self._tools.clear()


# Global tool registry instance
_global_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _global_tool_registry


def register_tool(name: str, description: str, func: Callable, **kwargs):
    """Convenience function to register a tool"""
    return _global_tool_registry.register_tool(name, description, func, **kwargs)


def execute_tool(name: str, *args, **kwargs) -> ToolResult:
    """Convenience function to execute a tool"""
    return _global_tool_registry.execute_tool(name, *args, **kwargs)


# Mock tools for testing
def mock_search_tool(query: str) -> Dict[str, Any]:
    """Mock search tool - returns fake results"""
    return {
        "query": query,
        "results": [
            {"title": f"Result 1 for {query}", "url": "https://example.com/1"},
            {"title": f"Result 2 for {query}", "url": "https://example.com/2"}
        ]
    }


def mock_browser_tool(url: str) -> Dict[str, Any]:
    """Mock browser tool - returns fake page content"""
    return {
        "url": url,
        "status_code": 200,
        "content": f"<html><body>Mock content for {url}</body></html>"
    }


def mock_file_tool(operation: str, path: str, content: Optional[str] = None) -> Dict[str, Any]:
    """Mock file tool - simulates file operations"""
    return {
        "operation": operation,
        "path": path,
        "success": True,
        "content": content if operation == "read" else None
    }


def mock_data_tool(action: str, data: Any = None) -> Dict[str, Any]:
    """Mock data tool - processes data"""
    return {
        "action": action,
        "processed_data": data,
        "timestamp": "2024-01-01T00:00:00Z"
    }


# Register mock tools on module load
def register_mock_tools():
    """Register all mock tools"""
    registry = get_tool_registry()
    
    registry.register_tool(
        name="mock_search",
        description="Mock search tool for testing",
        func=mock_search_tool,
        parameters={"query": {"type": "string", "required": True}}
    )
    
    registry.register_tool(
        name="mock_browser",
        description="Mock browser tool for testing",
        func=mock_browser_tool,
        parameters={"url": {"type": "string", "required": True}}
    )
    
    registry.register_tool(
        name="mock_file",
        description="Mock file tool for testing",
        func=mock_file_tool,
        parameters={
            "operation": {"type": "string", "required": True},
            "path": {"type": "string", "required": True},
            "content": {"type": "string", "required": False}
        }
    )
    
    registry.register_tool(
        name="mock_data",
        description="Mock data processing tool for testing",
        func=mock_data_tool,
        parameters={
            "action": {"type": "string", "required": True},
            "data": {"type": "any", "required": False}
        }
    )
