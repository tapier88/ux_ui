"""
Task Manifest - Manages task persistence history and recovery
"""
import json
import os
from typing import List, Optional, Dict, Any

from harness.core.time import utc_now_iso
from harness.core.git.models import TaskManifestEntry


class TaskManifest:
    """Manages the task manifest file for tracking task persistence"""
    
    def __init__(self, manifest_path: str = "TASK_MANIFEST.json"):
        self.manifest_path = os.path.abspath(manifest_path)
        self._entries: Dict[str, TaskManifestEntry] = {}
        self._load()
    
    def _load(self):
        """Load manifest from file"""
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get("tasks", []):
                        entry = TaskManifestEntry.from_dict(entry_data)
                        self._entries[entry.task_id] = entry
            except (json.JSONDecodeError, KeyError) as e:
                # Start fresh if file is corrupted
                self._entries = {}
    
    def _save(self):
        """Save manifest to file"""
        data = {
            "version": "1.0",
            "updated_at": utc_now_iso(),
            "tasks": [entry.to_dict() for entry in self._entries.values()]
        }
        with open(self.manifest_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_entry(self, entry: TaskManifestEntry):
        """Add or update a task entry"""
        self._entries[entry.task_id] = entry
        self._save()
    
    def update_entry(
        self,
        task_id: str,
        status: Optional[str] = None,
        tests_passed: Optional[bool] = None,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
        published: Optional[bool] = None,
        remote_verified: Optional[bool] = None,
    ):
        """Update specific fields of a task entry"""
        if task_id not in self._entries:
            # Create new entry
            entry = TaskManifestEntry(
                task_id=task_id,
                task_name=task_id,
                status=status or "pending",
            )
            self._entries[task_id] = entry
        
        entry = self._entries[task_id]
        
        if status is not None:
            entry.status = status
        if tests_passed is not None:
            entry.tests_passed = tests_passed
        if commit_sha is not None:
            entry.commit_sha = commit_sha
        if branch is not None:
            entry.branch = branch
        if published is not None:
            entry.published = published
        if remote_verified is not None:
            entry.remote_verified = remote_verified
        
        self._save()
    
    def get_entry(self, task_id: str) -> Optional[TaskManifestEntry]:
        """Get a task entry by ID"""
        return self._entries.get(task_id)
    
    def get_all_entries(self) -> List[TaskManifestEntry]:
        """Get all task entries"""
        return list(self._entries.values())
    
    def get_published_tasks(self) -> List[TaskManifestEntry]:
        """Get all published tasks"""
        return [e for e in self._entries.values() if e.published]
    
    def get_verified_tasks(self) -> List[TaskManifestEntry]:
        """Get all remotely verified tasks"""
        return [e for e in self._entries.values() if e.remote_verified]
    
    def get_incomplete_tasks(self) -> List[TaskManifestEntry]:
        """Get all incomplete tasks"""
        return [
            e for e in self._entries.values() 
            if not e.remote_verified or e.status != "COMPLETE"
        ]
    
    def can_complete_task(self, task_id: str) -> bool:
        """Check if a task can be marked as complete"""
        entry = self._entries.get(task_id)
        if not entry:
            return False
        return entry.published and entry.remote_verified
    
    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task as complete if conditions are met"""
        if not self.can_complete_task(task_id):
            return False
        
        self.update_entry(task_id, status="COMPLETE")
        return True
    
    def recover_from_manifest(self) -> Dict[str, Any]:
        """
        Recover state from manifest after restart.
        Returns information about task states for recovery.
        """
        published = self.get_published_tasks()
        verified = self.get_verified_tasks()
        incomplete = self.get_incomplete_tasks()
        
        return {
            "total_tasks": len(self._entries),
            "published_count": len(published),
            "verified_count": len(verified),
            "incomplete_count": len(incomplete),
            "published_tasks": [e.task_id for e in published],
            "verified_tasks": [e.task_id for e in verified],
            "incomplete_tasks": [e.task_id for e in incomplete],
        }
    
    def clear(self):
        """Clear all entries"""
        self._entries.clear()
        self._save()
