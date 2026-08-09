"""
Checkpoint Storage - Persistent storage for checkpoints (CRITICAL-003 fix)

Checkpoints were previously in-memory only, meaning all progress was lost
on process restart or crash. This module adds a pluggable storage
interface so checkpoints survive restarts, with a JSON-file-based
implementation as the default (no external dependencies required).

Usage:
    from harness.core.state.storage import FileCheckpointStorage
    from harness.core.state import get_state_manager

    storage = FileCheckpointStorage(base_dir="harness/.data/checkpoints")
    get_state_manager().attach_checkpoint_storage(storage)
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import threading


class CheckpointStorage(ABC):
    """Abstract interface for persisting checkpoints."""

    @abstractmethod
    def save(self, checkpoint_dict: Dict[str, Any]) -> None:
        """Persist a checkpoint (already serialized via Checkpoint.to_dict())."""
        raise NotImplementedError

    @abstractmethod
    def load(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a single checkpoint by id, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def load_all_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        """Load all checkpoints for a task, ordered by creation order."""
        raise NotImplementedError

    @abstractmethod
    def delete_all_for_task(self, task_id: str) -> None:
        """Remove all persisted checkpoints for a task (cleanup)."""
        raise NotImplementedError


class InMemoryCheckpointStorage(CheckpointStorage):
    """Default no-op-equivalent storage: same lifetime as the process.

    This preserves the original V0.1 behavior exactly, so existing code
    that never attaches a storage backend keeps working unchanged.
    """

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def save(self, checkpoint_dict: Dict[str, Any]) -> None:
        with self._lock:
            self._data[checkpoint_dict["checkpoint_id"]] = checkpoint_dict

    def load(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._data.get(checkpoint_id)

    def load_all_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            matches = [c for c in self._data.values() if c.get("task_id") == task_id]
        matches.sort(key=lambda c: c.get("timestamp", ""))
        return matches

    def delete_all_for_task(self, task_id: str) -> None:
        with self._lock:
            to_delete = [cid for cid, c in self._data.items() if c.get("task_id") == task_id]
            for cid in to_delete:
                del self._data[cid]


class FileCheckpointStorage(CheckpointStorage):
    """JSON-file-based persistent checkpoint storage.

    Layout: ``{base_dir}/{task_id}/{checkpoint_id}.json``

    Writes are atomic (write to a temp file, then os.replace) to avoid
    corrupting a checkpoint if the process is killed mid-write.
    """

    def __init__(self, base_dir: str = "harness/.data/checkpoints"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _task_dir(self, task_id: str) -> Path:
        # task_id could theoretically contain path-unsafe characters;
        # keep it simple but defensive.
        safe_task_id = "".join(c for c in task_id if c.isalnum() or c in ("-", "_", "."))
        d = self.base_dir / (safe_task_id or "unknown_task")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save(self, checkpoint_dict: Dict[str, Any]) -> None:
        task_dir = self._task_dir(checkpoint_dict["task_id"])
        target = task_dir / f"{checkpoint_dict['checkpoint_id']}.json"
        tmp = target.with_suffix(".json.tmp")
        with self._lock:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(checkpoint_dict, f, indent=2)
            tmp.replace(target)

    def load(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        # checkpoint_id encodes task_id as its prefix (chk_{task_id}_{node_id}_{n})
        # but to stay robust we search all task directories.
        for task_dir in self.base_dir.iterdir() if self.base_dir.exists() else []:
            candidate = task_dir / f"{checkpoint_id}.json"
            if candidate.exists():
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    def load_all_for_task(self, task_id: str) -> List[Dict[str, Any]]:
        task_dir = self._task_dir(task_id)
        checkpoints = []
        for path in sorted(task_dir.glob("*.json")):
            with open(path, "r", encoding="utf-8") as f:
                checkpoints.append(json.load(f))
        checkpoints.sort(key=lambda c: c.get("timestamp", ""))
        return checkpoints

    def delete_all_for_task(self, task_id: str) -> None:
        task_dir = self._task_dir(task_id)
        if task_dir.exists():
            for path in task_dir.glob("*.json"):
                path.unlink()
