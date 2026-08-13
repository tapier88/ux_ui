"""
Git Persistence Models - State definitions for Git-based task persistence
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from harness.core.time import utc_now_iso


class TaskPersistenceState(Enum):
    """States for task persistence lifecycle"""
    IMPLEMENTING = "IMPLEMENTING"
    TESTING = "TESTING"
    READY_TO_COMMIT = "READY_TO_COMMIT"
    COMMITTED = "COMMITTED"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHED = "PUBLISHED"
    VERIFIED = "VERIFIED"
    INCOMPLETE = "INCOMPLETE"
    FAILED = "FAILED"
    
    # Final state - only reachable after PUBLISHED + VERIFIED
    COMPLETE = "COMPLETE"


class PublicationStatus(Enum):
    """Publication status of a commit"""
    NOT_STARTED = "NOT_STARTED"
    LOCAL_COMMITTED = "LOCAL_COMMITTED"
    PUBLISHING = "PUBLISHING"
    REMOTE_PUBLISHED = "REMOTE_PUBLISHED"
    REMOTE_VERIFIED = "REMOTE_VERIFIED"
    PUBLICATION_FAILED = "PUBLICATION_FAILED"
    PUBLICATION_REQUIRED = "PUBLICATION_REQUIRED"


@dataclass
class GitStatus:
    """Represents the current Git repository status"""
    repository: Optional[str] = None
    current_branch: Optional[str] = None
    remote: Optional[str] = None
    has_uncommitted_changes: bool = False
    has_staged_changes: bool = False
    has_untracked_files: bool = False
    uncommitted_files: List[str] = field(default_factory=list)
    staged_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    last_commit_message: Optional[str] = None
    last_commit_sha: Optional[str] = None
    last_commit_timestamp: Optional[str] = None
    ahead_count: int = 0
    behind_count: int = 0
    is_clean: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository": self.repository,
            "current_branch": self.current_branch,
            "remote": self.remote,
            "has_uncommitted_changes": self.has_uncommitted_changes,
            "has_staged_changes": self.has_staged_changes,
            "has_untracked_files": self.has_untracked_files,
            "uncommitted_files": self.uncommitted_files,
            "staged_files": self.staged_files,
            "untracked_files": self.untracked_files,
            "last_commit_message": self.last_commit_message,
            "last_commit_sha": self.last_commit_sha,
            "last_commit_timestamp": self.last_commit_timestamp,
            "ahead_count": self.ahead_count,
            "behind_count": self.behind_count,
            "is_clean": self.is_clean,
        }


@dataclass
class CommitInfo:
    """Information about a Git commit"""
    sha: str
    message: str
    author: str
    timestamp: str
    branch: str
    files_changed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sha": self.sha,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp,
            "branch": self.branch,
            "files_changed": self.files_changed,
        }


@dataclass
class TaskManifestEntry:
    """Entry in the task manifest"""
    task_id: str
    task_name: str
    status: str
    tests_passed: bool = False
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    published: bool = False
    remote_verified: bool = False
    timestamp: str = field(default_factory=utc_now_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status,
            "tests": "passed" if self.tests_passed else "failed",
            "commit_sha": self.commit_sha or "",
            "branch": self.branch or "",
            "published": self.published,
            "remote_verified": self.remote_verified,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskManifestEntry":
        return cls(
            task_id=data.get("task_id", ""),
            task_name=data.get("task_name", ""),
            status=data.get("status", ""),
            tests_passed=data.get("tests") == "passed",
            commit_sha=data.get("commit_sha"),
            branch=data.get("branch"),
            published=data.get("published", False),
            remote_verified=data.get("remote_verified", False),
            timestamp=data.get("timestamp", utc_now_iso()),
        )
