"""
State Engine - Shared state management across nodes
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import copy


@dataclass
class Checkpoint:
    """Represents a state checkpoint"""
    checkpoint_id: str
    task_id: str
    node_id: str
    timestamp: str
    state_snapshot: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "node_id": self.node_id,
            "timestamp": self.timestamp,
            "state_snapshot": self.state_snapshot
        }


@dataclass 
class TaskState:
    """Represents the state of a task"""
    task_id: str
    status: str = "pending"  # pending, running, completed, failed
    current_node: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: List[Checkpoint] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "current_node": self.current_node,
            "metadata": self.metadata,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "history": self.history,
            "errors": self.errors,
            "checkpoints": [c.to_dict() for c in self.checkpoints],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def add_to_history(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Add an entry to the history"""
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "data": data or {}
        })
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_error(self, node_id: str, error: str, details: Optional[Dict[str, Any]] = None):
        """Record an error"""
        self.errors.append({
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": node_id,
            "error": error,
            "details": details or {}
        })
        self.updated_at = datetime.utcnow().isoformat()
    
    def create_checkpoint(self, node_id: str) -> Checkpoint:
        """Create a checkpoint of the current state"""
        checkpoint_id = f"chk_{self.task_id}_{node_id}_{len(self.checkpoints)}"
        snapshot = {
            "outputs": copy.deepcopy(self.outputs),
            "metadata": copy.deepcopy(self.metadata),
            "history": copy.deepcopy(self.history)
        }
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            task_id=self.task_id,
            node_id=node_id,
            timestamp=datetime.utcnow().isoformat(),
            state_snapshot=snapshot
        )
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def restore_from_checkpoint(self, checkpoint: Checkpoint):
        """Restore state from a checkpoint"""
        self.outputs = checkpoint.state_snapshot.get("outputs", {})
        self.metadata = checkpoint.state_snapshot.get("metadata", {})
        self.history = checkpoint.state_snapshot.get("history", [])
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_last_checkpoint(self) -> Optional[Checkpoint]:
        """Get the last checkpoint"""
        if self.checkpoints:
            return self.checkpoints[-1]
        return None


class StateManager:
    """Manages state for all tasks"""
    
    def __init__(self):
        self._states: Dict[str, TaskState] = {}
        self._checkpoint_store: Dict[str, Checkpoint] = {}
    
    def create_state(self, task_id: str, **kwargs) -> TaskState:
        """Create a new task state"""
        state = TaskState(task_id=task_id, **kwargs)
        self._states[task_id] = state
        return state
    
    def get_state(self, task_id: str) -> Optional[TaskState]:
        """Get state for a task"""
        return self._states.get(task_id)
    
    def update_state(self, task_id: str, **updates) -> Optional[TaskState]:
        """Update state for a task"""
        state = self._states.get(task_id)
        if state:
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            state.updated_at = datetime.utcnow().isoformat()
        return state
    
    def delete_state(self, task_id: str):
        """Delete state for a task"""
        if task_id in self._states:
            del self._states[task_id]
    
    def save_checkpoint(self, state: TaskState, node_id: str) -> Checkpoint:
        """Save a checkpoint for a task"""
        checkpoint = state.create_checkpoint(node_id)
        self._checkpoint_store[checkpoint.checkpoint_id] = checkpoint
        return checkpoint
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get a specific checkpoint"""
        return self._checkpoint_store.get(checkpoint_id)
    
    def get_last_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """Get the last checkpoint for a task"""
        state = self._states.get(task_id)
        if state:
            return state.get_last_checkpoint()
        return None
    
    def restore_from_last_checkpoint(self, task_id: str) -> bool:
        """Restore state from the last checkpoint"""
        state = self._states.get(task_id)
        if state:
            checkpoint = state.get_last_checkpoint()
            if checkpoint:
                state.restore_from_checkpoint(checkpoint)
                return True
        return False
    
    def list_states(self) -> List[str]:
        """List all task IDs"""
        return list(self._states.keys())
    
    def clear_all(self):
        """Clear all states and checkpoints"""
        self._states.clear()
        self._checkpoint_store.clear()


# Global state manager instance
_global_state_manager = StateManager()


def get_state_manager() -> StateManager:
    """Get the global state manager"""
    return _global_state_manager
