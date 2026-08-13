"""
State Engine - Shared state management across nodes
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json
import copy
import uuid

from harness.core.time import utc_now_iso


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
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    
    # Git persistence fields
    git_commit_sha: Optional[str] = None
    git_branch: Optional[str] = None
    git_remote: Optional[str] = None
    git_publication_status: Optional[str] = None
    git_remote_verified: bool = False
    
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
            "updated_at": self.updated_at,
            # Git persistence fields
            "git_commit_sha": self.git_commit_sha,
            "git_branch": self.git_branch,
            "git_remote": self.git_remote,
            "git_publication_status": self.git_publication_status,
            "git_remote_verified": self.git_remote_verified,
        }
    
    def add_to_history(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Add an entry to the history"""
        self.history.append({
            "timestamp": utc_now_iso(),
            "action": action,
            "data": data or {}
        })
        self.updated_at = utc_now_iso()
    
    def add_error(self, node_id: str, error: str, details: Optional[Dict[str, Any]] = None):
        """Record an error"""
        self.errors.append({
            "timestamp": utc_now_iso(),
            "node_id": node_id,
            "error": error,
            "details": details or {}
        })
        self.updated_at = utc_now_iso()
    
    def create_checkpoint(self, node_id: str) -> Checkpoint:
        """Create a checkpoint of the current state.

        MED-007 fix: checkpoint IDs previously used a predictable
        `chk_{task_id}_{node_id}_{index}` format where the index could
        collide if the checkpoint list was ever trimmed/reset. A short
        uuid suffix is appended to guarantee uniqueness while keeping the
        id human-readable for debugging.
        """
        checkpoint_id = f"chk_{self.task_id}_{node_id}_{len(self.checkpoints)}_{uuid.uuid4().hex[:8]}"
        snapshot = {
            "outputs": copy.deepcopy(self.outputs),
            "metadata": copy.deepcopy(self.metadata),
            "history": copy.deepcopy(self.history),
            "inputs": copy.deepcopy(self.inputs),
            "current_node": self.current_node,
            "status": self.status,
            "errors": copy.deepcopy(self.errors),
        }
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            task_id=self.task_id,
            node_id=node_id,
            timestamp=utc_now_iso(),
            state_snapshot=snapshot
        )
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def restore_from_checkpoint(self, checkpoint: Checkpoint):
        """Restore state from a checkpoint.

        MED-003 fix: previously only outputs/metadata/history were
        restored, silently leaving inputs/current_node/status/errors
        stale and inconsistent with the rest of the restored state.
        All snapshot fields are now restored.
        """
        self.outputs = checkpoint.state_snapshot.get("outputs", {})
        self.metadata = checkpoint.state_snapshot.get("metadata", {})
        self.history = checkpoint.state_snapshot.get("history", [])
        self.inputs = checkpoint.state_snapshot.get("inputs", self.inputs)
        self.current_node = checkpoint.state_snapshot.get("current_node", self.current_node)
        self.status = checkpoint.state_snapshot.get("status", self.status)
        self.errors = checkpoint.state_snapshot.get("errors", self.errors)
        self.updated_at = utc_now_iso()
    
    def get_last_checkpoint(self) -> Optional[Checkpoint]:
        """Get the last checkpoint"""
        if self.checkpoints:
            return self.checkpoints[-1]
        return None


class StateManager:
    """Manages state for all tasks.

    By default checkpoints are in-memory only, identical to the original
    V0.1 behavior. Call ``attach_checkpoint_storage()`` with a
    ``CheckpointStorage`` implementation (see
    ``harness.core.state.storage``) to make checkpoints survive process
    restarts — this is opt-in so existing code and tests are unaffected.
    """

    def __init__(self):
        self._states: Dict[str, TaskState] = {}
        self._checkpoint_store: Dict[str, Checkpoint] = {}
        self._persistent_storage = None  # CheckpointStorage, if attached
    
    def attach_checkpoint_storage(self, storage):
        """Attach a CheckpointStorage backend for persistent checkpoints."""
        self._persistent_storage = storage

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
            state.updated_at = utc_now_iso()
        return state
    
    def delete_state(self, task_id: str):
        """Delete state for a task"""
        if task_id in self._states:
            del self._states[task_id]
    
    def save_checkpoint(self, state: TaskState, node_id: str) -> Checkpoint:
        """Save a checkpoint for a task (and persist it, if storage attached)"""
        checkpoint = state.create_checkpoint(node_id)
        self._checkpoint_store[checkpoint.checkpoint_id] = checkpoint
        if self._persistent_storage is not None:
            self._persistent_storage.save(checkpoint.to_dict())
        return checkpoint
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get a specific checkpoint (memory first, falling back to persistent storage)"""
        cached = self._checkpoint_store.get(checkpoint_id)
        if cached is not None:
            return cached
        if self._persistent_storage is not None:
            data = self._persistent_storage.load(checkpoint_id)
            if data:
                return self._checkpoint_from_dict(data)
        return None
    
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

    def restore_task_from_persistent_storage(self, task_id: str) -> Optional[TaskState]:
        """Recreate a TaskState from persisted checkpoints after a restart.

        This is the actual crash-recovery path (CRITICAL-003): if the
        process died, ``self._states`` is empty, but the checkpoints on
        disk are not. This rebuilds an in-memory TaskState from the most
        recent persisted checkpoint so execution can resume.
        """
        if self._persistent_storage is None:
            return None

        checkpoint_dicts = self._persistent_storage.load_all_for_task(task_id)
        if not checkpoint_dicts:
            return None

        checkpoints = [self._checkpoint_from_dict(d) for d in checkpoint_dicts]
        latest = checkpoints[-1]

        state = TaskState(task_id=task_id, status=latest.state_snapshot.get("status", "running"))
        state.checkpoints = checkpoints
        state.restore_from_checkpoint(latest)
        self._states[task_id] = state
        return state

    @staticmethod
    def _checkpoint_from_dict(data: Dict[str, Any]) -> Checkpoint:
        return Checkpoint(
            checkpoint_id=data["checkpoint_id"],
            task_id=data["task_id"],
            node_id=data["node_id"],
            timestamp=data["timestamp"],
            state_snapshot=data.get("state_snapshot", {}),
        )
    
    def list_states(self) -> List[str]:
        """List all task IDs"""
        return list(self._states.keys())
    
    def clear_all(self):
        """Clear all states and checkpoints (in-memory only — does not
        touch persistent storage; use the storage backend's own cleanup
        methods to purge disk-backed checkpoints)."""
        self._states.clear()
        self._checkpoint_store.clear()


# Global state manager instance
_global_state_manager = StateManager()


def get_state_manager() -> StateManager:
    """Get the global state manager"""
    return _global_state_manager
