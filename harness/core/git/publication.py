"""
Git Publication - Handles publishing commits to remote repository
"""
import subprocess
import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from harness.core.git.models import PublicationStatus, CommitInfo
from harness.core.git.inspector import GitInspector
from harness.core.events import emit_event, EventType


class GitPublicationProvider(ABC):
    """Abstract base class for Git publication providers"""
    
    @abstractmethod
    def prepare_publication(self) -> bool:
        """Prepare for publication (e.g., fetch, check branch)"""
        pass
    
    @abstractmethod
    def publish(self) -> bool:
        """Publish local commits to remote"""
        pass
    
    @abstractmethod
    def get_publication_status(self) -> PublicationStatus:
        """Get current publication status"""
        pass
    
    @abstractmethod
    def verify_remote_commit(self, commit_sha: str) -> bool:
        """Verify that a specific commit exists on the remote"""
        pass


class LocalPublicationProvider(GitPublicationProvider):
    """
    Local publication provider - attempts to push to remote.
    In environments where direct push is not available, this will
    signal PUBLICATION_REQUIRED instead of failing.
    """
    
    def __init__(self, repo_path: str = ".", inspector: Optional[GitInspector] = None):
        self.repo_path = os.path.abspath(repo_path)
        self.inspector = inspector or GitInspector(repo_path)
        self._last_status = PublicationStatus.NOT_STARTED
        self._push_available = True  # Will be set based on first attempt
    
    def _run_git(self, args: list) -> Tuple[bool, str, str]:
        """Run a Git command and return (success, stdout, stderr)"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Git command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def prepare_publication(self) -> bool:
        """Prepare for publication by fetching from remote"""
        emit_event(
            EventType.PUBLICATION_STARTED,
            task_id="system",
            data={"action": "prepare_publication"},
        )
        
        # Fetch latest from remote
        success, _, stderr = self._run_git(["fetch", "origin"])
        if not success:
            # Remote may not be accessible in this environment
            self._push_available = False
            self._last_status = PublicationStatus.PUBLICATION_REQUIRED
            return False
        
        self._push_available = True
        return True
    
    def publish(self) -> bool:
        """Attempt to publish local commits to remote"""
        if not self._push_available:
            # Environment doesn't support direct push
            self._last_status = PublicationStatus.PUBLICATION_REQUIRED
            emit_event(
                EventType.PUBLICATION_REQUIRED,
                task_id="system",
                data={"reason": "environment_does_not_support_direct_push"},
            )
            return False
        
        emit_event(
            EventType.PUBLICATION_STARTED,
            task_id="system",
            data={"action": "publish"},
        )
        
        branch = self.inspector.get_current_branch()
        if not branch:
            self._last_status = PublicationStatus.PUBLICATION_FAILED
            return False
        
        # Attempt to push
        success, stdout, stderr = self._run_git([
            "push", "-u", "origin", branch
        ])
        
        if success:
            self._last_status = PublicationStatus.REMOTE_PUBLISHED
            emit_event(
                EventType.PUBLICATION_COMPLETED,
                task_id="system",
                data={"branch": branch},
            )
            return True
        else:
            # Check if it's an auth/permission error
            if any(err in stderr.lower() for err in [
                "permission denied",
                "authentication",
                "authorization",
                "forbidden",
                "could not read from remote",
            ]):
                self._last_status = PublicationStatus.PUBLICATION_REQUIRED
                emit_event(
                    EventType.PUBLICATION_REQUIRED,
                    task_id="system",
                    data={"reason": "authentication_required", "error": stderr},
                )
                return False
            
            self._last_status = PublicationStatus.PUBLICATION_FAILED
            return False
    
    def get_publication_status(self) -> PublicationStatus:
        """Get current publication status"""
        if self._last_status == PublicationStatus.NOT_STARTED:
            # Check current state
            ahead, behind = self.inspector.get_ahead_behind()
            if ahead > 0:
                self._last_status = PublicationStatus.LOCAL_COMMITTED
            elif behind > 0:
                self._last_status = PublicationStatus.REMOTE_VERIFIED
            else:
                self._last_status = PublicationStatus.REMOTE_VERIFIED
        
        return self._last_status
    
    def verify_remote_commit(self, commit_sha: str) -> bool:
        """Verify that a specific commit exists on the remote"""
        branch = self.inspector.get_current_branch()
        if not branch:
            return False
        
        # Fetch to ensure we have latest remote info
        self._run_git(["fetch", "origin"])
        
        # Check if commit exists on remote branch
        success, stdout, _ = self._run_git([
            "merge-base", "--is-ancestor", commit_sha, f"origin/{branch}"
        ])
        
        if success:
            self._last_status = PublicationStatus.REMOTE_VERIFIED
            emit_event(
                EventType.REMOTE_COMMIT_VERIFIED,
                task_id="system",
                data={"commit_sha": commit_sha, "branch": branch},
            )
            return True
        
        return False
    
    def check_remote_exists(self) -> bool:
        """Check if remote repository is accessible"""
        success, _, _ = self._run_git(["ls-remote", "origin", "HEAD"])
        return success
