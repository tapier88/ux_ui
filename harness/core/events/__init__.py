"""
Event System - Core event definitions and emitter
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import json

from harness.core.time import utc_now_iso


class EventType(Enum):
    TASK_STARTED = "TASK_STARTED"
    NODE_STARTED = "NODE_STARTED"
    NODE_COMPLETED = "NODE_COMPLETED"
    NODE_FAILED = "NODE_FAILED"
    TOOL_STARTED = "TOOL_STARTED"
    TOOL_COMPLETED = "TOOL_COMPLETED"
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    STATE_UPDATED = "STATE_UPDATED"
    ERROR_RECOVERED = "ERROR_RECOVERED"
    # Git persistence events
    GIT_STATUS_CHECKED = "GIT_STATUS_CHECKED"
    COMMIT_CREATED = "COMMIT_CREATED"
    PUBLICATION_REQUIRED = "PUBLICATION_REQUIRED"
    PUBLICATION_STARTED = "PUBLICATION_STARTED"
    PUBLICATION_COMPLETED = "PUBLICATION_COMPLETED"
    REMOTE_COMMIT_VERIFIED = "REMOTE_COMMIT_VERIFIED"
    TASK_PERSISTENCE_FAILED = "TASK_PERSISTENCE_FAILED"
    # Governance events (design elevation gate — see harness/core/governance)
    GATE_EVALUATED = "GATE_EVALUATED"
    GATE_APPROVED = "GATE_APPROVED"
    GATE_BLOCKED = "GATE_BLOCKED"
    SCORE_TOO_LOW = "SCORE_TOO_LOW"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


@dataclass
class Event:
    """Represents a system event"""
    event_type: EventType
    task_id: str
    timestamp: str = field(default_factory=utc_now_iso)
    node_id: Optional[str] = None
    status: str = "info"
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "status": self.status,
            "data": self.data or {},
            "error": self.error
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventEmitter:
    """Event emitter for broadcasting system events"""
    
    def __init__(self):
        self._listeners: List[callable] = []
        self._event_history: List[Event] = []
    
    def subscribe(self, callback: callable):
        """Subscribe to events"""
        self._listeners.append(callback)
    
    def unsubscribe(self, callback: callable):
        """Unsubscribe from events"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def emit(self, event: Event):
        """Emit an event to all listeners"""
        self._event_history.append(event)
        for listener in self._listeners:
            try:
                listener(event)
            except Exception as e:
                # Don't let listener errors break the system
                pass
    
    def get_history(self, task_id: Optional[str] = None) -> List[Event]:
        """Get event history, optionally filtered by task_id"""
        if task_id:
            return [e for e in self._event_history if e.task_id == task_id]
        return self._event_history
    
    def clear_history(self):
        """Clear event history"""
        self._event_history.clear()


# Global event emitter instance
_global_emitter = EventEmitter()


def get_emitter() -> EventEmitter:
    """Get the global event emitter"""
    return _global_emitter


def emit_event(event_type: EventType, task_id: str, **kwargs):
    """Convenience function to emit an event"""
    event = Event(event_type=event_type, task_id=task_id, **kwargs)
    _global_emitter.emit(event)
    return event
