"""
Runtime - Graph execution engine with error handling and checkpoints
"""
from typing import Dict, Any, Optional, List, Callable
import logging
from datetime import datetime

from harness.core.graph import Graph, Node, NodeType
from harness.core.state import TaskState, StateManager, get_state_manager
from harness.core.events import (
    EventType, EventEmitter, Event, 
    get_emitter, emit_event
)


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result of graph execution"""
    
    def __init__(self, success: bool, task_id: str):
        self.success = success
        self.task_id = task_id
        self.nodes_executed: List[str] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time: str = datetime.utcnow().isoformat()
        self.end_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "task_id": self.task_id,
            "nodes_executed": self.nodes_executed,
            "errors": self.errors,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class RuntimeConfig:
    """Configuration for runtime execution"""
    
    def __init__(self):
        self.max_retries: int = 3
        self.retry_delay: float = 1.0
        self.enable_checkpoints: bool = True
        self.stop_on_error: bool = False
        self.timeout_seconds: Optional[int] = None


class GraphRuntime:
    """Runtime engine for executing graphs"""
    
    def __init__(self, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self.state_manager = get_state_manager()
        self.emitter = get_emitter()
        self._node_handlers: Dict[str, Callable] = {}
    
    def register_node_handler(self, node_id: str, handler: Callable):
        """Register a custom handler for a node"""
        self._node_handlers[node_id] = handler
    
    def execute(self, graph: Graph, task_id: str, 
                initial_state: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Execute a graph"""
        result = ExecutionResult(success=False, task_id=task_id)
        
        # Validate graph first
        is_valid, errors = graph.validate()
        if not is_valid:
            logger.error(f"Graph validation failed: {errors}")
            result.errors.append({"type": "validation", "errors": errors})
            return result
        
        # Create initial state
        state = self.state_manager.create_state(
            task_id=task_id,
            status="running",
            inputs=initial_state or {},
            metadata={"graph_name": graph.name}
        )
        
        # Emit task started event
        emit_event(EventType.TASK_STARTED, task_id=task_id)
        logger.info(f"Task {task_id} started")
        
        try:
            # Start from START node
            current_node_id = graph.start_node
            
            while current_node_id:
                node = graph.get_node(current_node_id)
                if not node:
                    break
                
                # Execute node
                success, next_node_id = self._execute_node(
                    node, state, graph, result
                )
                
                if not success:
                    if self.config.stop_on_error:
                        break
                    # Try to continue to END if possible
                    if graph.end_node:
                        current_node_id = graph.end_node
                    else:
                        break
                else:
                    current_node_id = next_node_id
            
            # Mark task as completed
            state.status = "completed"
            result.success = True
            
            # Emit task completed event
            emit_event(
                EventType.TASK_COMPLETED, 
                task_id=task_id,
                status="success",
                data=result.to_dict()
            )
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            state.status = "failed"
            state.add_error("runtime", str(e))
            result.errors.append({"type": "runtime", "error": str(e)})
            
            # Emit task failed event
            emit_event(
                EventType.TASK_FAILED,
                task_id=task_id,
                status="error",
                error=str(e)
            )
            logger.error(f"Task {task_id} failed: {e}")
        
        result.end_time = datetime.utcnow().isoformat()
        return result
    
    def _execute_node(self, node: Node, state: TaskState, 
                     graph: Graph, result: ExecutionResult) -> tuple[bool, Optional[str]]:
        """Execute a single node with error handling"""
        
        # Emit node started event
        emit_event(
            EventType.NODE_STARTED,
            task_id=state.task_id,
            node_id=node.id
        )
        logger.info(f"Executing node: {node.id}")
        
        state.current_node = node.id
        retries = 0
        last_error = None
        
        while retries < self.config.max_retries:
            try:
                # Execute the node
                output = self._run_node_execution(node, state)
                
                # Store output
                state.outputs[node.id] = output
                state.add_to_history(f"node_completed:{node.id}", {"output": output})
                
                # Create checkpoint after successful execution
                if self.config.enable_checkpoints:
                    self.state_manager.save_checkpoint(state, node.id)
                    emit_event(
                        EventType.CHECKPOINT_CREATED,
                        task_id=state.task_id,
                        node_id=node.id,
                        data={"checkpoint_id": f"chk_{state.task_id}_{node.id}"}
                    )
                
                # Emit node completed event
                emit_event(
                    EventType.NODE_COMPLETED,
                    task_id=state.task_id,
                    node_id=node.id,
                    status="success"
                )
                
                result.nodes_executed.append(node.id)
                
                # Get next node(s)
                next_nodes = graph.get_next_nodes(node.id, state)
                next_node_id = next_nodes[0] if next_nodes else None
                
                # Handle END node
                if node.node_type == NodeType.END:
                    return True, None
                
                return True, next_node_id
                
            except Exception as e:
                last_error = e
                retries += 1
                logger.warning(f"Node {node.id} failed (attempt {retries}): {e}")
                
                if retries < self.config.max_retries:
                    # Retry delay could be implemented here
                    continue
        
        # All retries exhausted
        state.add_error(node.id, str(last_error))
        
        # Emit node failed event
        emit_event(
            EventType.NODE_FAILED,
            task_id=state.task_id,
            node_id=node.id,
            status="error",
            error=str(last_error)
        )
        
        result.errors.append({
            "node_id": node.id,
            "error": str(last_error),
            "retries": retries
        })
        
        return False, None
    
    def _run_node_execution(self, node: Node, state: TaskState) -> Any:
        """Run the actual node execution"""
        
        # Check for custom handler
        if node.id in self._node_handlers:
            return self._node_handlers[node.id](state)
        
        # Use node's execute function
        if node.execute_func:
            return node.execute_func(state)
        
        # Default behavior for START/END nodes
        if node.node_type == NodeType.START:
            return {"started": True, "timestamp": datetime.utcnow().isoformat()}
        elif node.node_type == NodeType.END:
            return {"ended": True, "timestamp": datetime.utcnow().isoformat()}
        
        return None
    
    def restore_from_checkpoint(self, task_id: str) -> Optional[TaskState]:
        """Restore a task from its last checkpoint"""
        state = self.state_manager.get_state(task_id)
        if not state:
            return None
        
        restored = self.state_manager.restore_from_last_checkpoint(task_id)
        if restored:
            logger.info(f"Task {task_id} restored from checkpoint")
            emit_event(
                EventType.ERROR_RECOVERED,
                task_id=task_id,
                data={"restored_from": "checkpoint"}
            )
        
        return self.state_manager.get_state(task_id)


# Global runtime instance
_default_runtime = GraphRuntime()


def get_runtime() -> GraphRuntime:
    """Get the default runtime"""
    return _default_runtime


def execute_graph(graph: Graph, task_id: str, 
                  initial_state: Optional[Dict[str, Any]] = None) -> ExecutionResult:
    """Convenience function to execute a graph"""
    return _default_runtime.execute(graph, task_id, initial_state)
