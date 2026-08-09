"""
Git Persistence - Handles commit creation and Git state management
"""
import subprocess
import os
from typing import Optional, List, Tuple
from datetime import datetime

from harness.core.git.models import CommitInfo, TaskPersistenceState, PublicationStatus
from harness.core.git.inspector import GitInspector
from harness.core.events import emit_event, EventType


class GitPersistence:
    """Handles Git commit operations and persistence state"""
    
    def __init__(self, repo_path: str = ".", inspector: Optional[GitInspector] = None):
        self.repo_path = os.path.abspath(repo_path)
        self.inspector = inspector or GitInspector(repo_path)
    
    def _run_git(self, args: List[str]) -> Tuple[bool, str, str]:
        """Run a Git command and return (success, stdout, stderr)"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Git command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def stage_files(self, files: List[str]) -> bool:
        """Stage specific files for commit"""
        if not files:
            return True
        
        success, _, stderr = self._run_git(["add"] + files)
        if not success:
            return False
        return True
    
    def stage_all(self) -> bool:
        """Stage all changes"""
        success, _, _ = self._run_git(["add", "-A"])
        return success
    
    def create_commit(self, message: str, files: Optional[List[str]] = None) -> Optional[CommitInfo]:
        """Create a Git commit with the given message"""
        # Check for sensitive files first
        status = self.inspector.get_status()
        all_files = status.uncommitted_files + status.staged_files + status.untracked_files
        
        if files:
            all_files = files
        
        sensitive_files = self.inspector.contains_sensitive_files(all_files)
        if sensitive_files:
            raise ValueError(f"Cannot commit sensitive files: {sensitive_files}")
        
        # Stage files if specified
        if files:
            if not self.stage_files(files):
                return None
        else:
            if not self.stage_all():
                return None
        
        # Create commit
        success, stdout, stderr = self._run_git([
            "commit", "-m", message,
            "--author", "Harness <harness@local>"
        ])
        
        if not success:
            # May fail if nothing to commit
            if "nothing to commit" in stderr.lower() or "nothing to commit" in stdout.lower():
                # Return existing commit info
                sha, msg, ts = self.inspector.get_last_commit()
                if sha:
                    branch = self.inspector.get_current_branch()
                    return CommitInfo(
                        sha=sha,
                        message=msg or "",
                        author="Harness <harness@local>",
                        timestamp=ts or datetime.utcnow().isoformat(),
                        branch=branch or "",
                    )
            return None
        
        # Get commit info
        sha, msg, ts = self.inspector.get_last_commit()
        branch = self.inspector.get_current_branch()
        
        # Get changed files
        success, stdout, _ = self._run_git(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"])
        files_changed = []
        if success and stdout:
            files_changed = [f.strip() for f in stdout.split("\n") if f.strip()]
        
        commit_info = CommitInfo(
            sha=sha or "",
            message=message,
            author="Harness <harness@local>",
            timestamp=ts or datetime.utcnow().isoformat(),
            branch=branch or "",
            files_changed=files_changed,
        )
        
        # Emit event
        emit_event(
            EventType.COMMIT_CREATED,
            task_id="system",
            data={"commit_sha": commit_info.sha, "message": message},
        )
        
        return commit_info
    
    def get_current_commit_sha(self) -> Optional[str]:
        """Get the current HEAD commit SHA"""
        sha, _, _ = self.inspector.get_last_commit()
        return sha
    
    def has_changes(self) -> bool:
        """Check if there are any uncommitted changes"""
        status = self.inspector.get_status()
        return not status.is_clean
    
    def get_persistence_state(self) -> TaskPersistenceState:
        """Determine the current persistence state based on Git status"""
        status = self.inspector.get_status()
        
        if not status.repository:
            return TaskPersistenceState.FAILED
        
        if status.has_uncommitted_changes or status.has_untracked_files:
            return TaskPersistenceState.READY_TO_COMMIT
        
        if status.ahead_count > 0:
            return TaskPersistenceState.COMMITTED
        
        return TaskPersistenceState.READY_TO_PUBLISH
    
    def reset_staged(self) -> bool:
        """Unstage all staged changes"""
        success, _, _ = self._run_git(["reset", "HEAD"])
        return success
    
    def discard_uncommitted(self) -> bool:
        """Discard uncommitted changes"""
        success, _, _ = self._run_git(["checkout", "--", "."])
        return success
