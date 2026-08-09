"""
Git Validator - Validates Git state for task completion
"""
from typing import Tuple, Optional

from harness.core.git.models import (
    TaskPersistenceState, 
    PublicationStatus,
    GitStatus,
)
from harness.core.git.inspector import GitInspector
from harness.core.git.persistence import GitPersistence
from harness.core.git.publication import GitPublicationProvider
from harness.core.events import emit_event, EventType


class GitValidator:
    """Validates Git state for task completion requirements"""
    
    def __init__(
        self, 
        repo_path: str = ".",
        inspector: Optional[GitInspector] = None,
        persistence: Optional[GitPersistence] = None,
        publisher: Optional[GitPublicationProvider] = None,
    ):
        self.repo_path = repo_path
        self.inspector = inspector or GitInspector(repo_path)
        self.persistence = persistence or GitPersistence(repo_path, self.inspector)
        self.publisher = publisher  # Can be None for local-only validation
    
    def validate_commit_gate(
        self, 
        task_id: str,
        tests_passed: bool = True,
    ) -> Tuple[bool, str]:
        """
        Validate commit gate requirements before creating a commit.
        
        Returns:
            (success, message)
        """
        # Step 1: Verify tests passed
        if not tests_passed:
            emit_event(
                EventType.TASK_PERSISTENCE_FAILED,
                task_id=task_id,
                data={"reason": "tests_failed"},
            )
            return False, "Tests must pass before commit"
        
        # Step 2: Check for changes to commit
        status = self.inspector.get_status()
        
        if status.is_clean and not status.has_staged_changes:
            # No changes to commit - this is okay if we already have a commit
            return True, "No changes to commit"
        
        # Step 3: Check for sensitive files
        all_files = status.uncommitted_files + status.staged_files + status.untracked_files
        sensitive = self.inspector.contains_sensitive_files(all_files)
        
        if sensitive:
            emit_event(
                EventType.TASK_PERSISTENCE_FAILED,
                task_id=task_id,
                data={"reason": "sensitive_files_detected", "files": sensitive},
            )
            return False, f"Sensitive files detected: {sensitive}"
        
        emit_event(
            EventType.GIT_STATUS_CHECKED,
            task_id=task_id,
            data={"status": status.to_dict()},
        )
        
        return True, "Commit gate passed"
    
    def validate_publication_gate(
        self,
        task_id: str,
        commit_sha: str,
    ) -> Tuple[bool, str, PublicationStatus]:
        """
        Validate publication gate requirements.
        
        Returns:
            (success, message, publication_status)
        """
        if not self.publisher:
            # No publisher available - signal that publication is required
            emit_event(
                EventType.PUBLICATION_REQUIRED,
                task_id=task_id,
                data={
                    "commit_sha": commit_sha,
                    "reason": "no_publisher_available",
                },
            )
            return False, "Publication required - remote verification not available", PublicationStatus.PUBLICATION_REQUIRED
        
        # Check publication status
        pub_status = self.publisher.get_publication_status()
        
        if pub_status == PublicationStatus.PUBLICATION_REQUIRED:
            emit_event(
                EventType.PUBLICATION_REQUIRED,
                task_id=task_id,
                data={"commit_sha": commit_sha},
            )
            return False, "PUBLICATION_REQUIRED - Remote push needed", PublicationStatus.PUBLICATION_REQUIRED
        
        if pub_status in [PublicationStatus.NOT_STARTED, PublicationStatus.LOCAL_COMMITTED]:
            emit_event(
                EventType.PUBLICATION_REQUIRED,
                task_id=task_id,
                data={"commit_sha": commit_sha, "status": pub_status.value},
            )
            return False, "Commit exists locally but not published", PublicationStatus.LOCAL_COMMITTED
        
        # Verify remote commit
        if self.publisher.verify_remote_commit(commit_sha):
            emit_event(
                EventType.REMOTE_COMMIT_VERIFIED,
                task_id=task_id,
                data={"commit_sha": commit_sha},
            )
            return True, "Remote commit verified", PublicationStatus.REMOTE_VERIFIED
        
        emit_event(
            EventType.PUBLICATION_REQUIRED,
            task_id=task_id,
            data={"commit_sha": commit_sha},
        )
        return False, "Commit not found on remote", PublicationStatus.PUBLICATION_REQUIRED
    
    def can_complete_task(
        self,
        task_id: str,
        commit_sha: Optional[str] = None,
        tests_passed: bool = True,
    ) -> Tuple[bool, str, TaskPersistenceState]:
        """
        Determine if a task can be marked as COMPLETE.
        
        A task can only be COMPLETE if:
        1. Tests have passed
        2. Changes are committed
        3. Commit is published to remote
        4. Remote commit is verified
        
        Returns:
            (can_complete, reason, persistence_state)
        """
        # Check tests
        if not tests_passed:
            return False, "Tests must pass", TaskPersistenceState.FAILED
        
        # Get current status
        status = self.inspector.get_status()
        
        # Check for uncommitted changes
        if status.has_uncommitted_changes or status.has_untracked_files:
            return False, "Uncommitted changes exist", TaskPersistenceState.READY_TO_COMMIT
        
        # Check if we have a commit
        current_sha = self.persistence.get_current_commit_sha()
        if not current_sha:
            return False, "No commit found", TaskPersistenceState.FAILED
        
        # If commit_sha provided, verify it matches
        if commit_sha and commit_sha != current_sha:
            return False, f"Commit SHA mismatch: expected {commit_sha}, got {current_sha}", TaskPersistenceState.COMMITTED
        
        # Check publication status
        if self.publisher:
            pub_success, pub_msg, pub_status = self.validate_publication_gate(task_id, current_sha)
            
            if not pub_success:
                if pub_status == PublicationStatus.PUBLICATION_REQUIRED:
                    return False, "INCOMPLETE — GITHUB PUBLICATION REQUIRED", TaskPersistenceState.INCOMPLETE
                return False, pub_msg, TaskPersistenceState.COMMITTED
            
            # Publication verified
            return True, "Task complete - published and verified", TaskPersistenceState.COMPLETE
        
        # No publisher - require external publication
        return False, "INCOMPLETE — GITHUB PUBLICATION REQUIRED", TaskPersistenceState.INCOMPLETE
    
    def get_completion_report(self, task_id: str) -> dict:
        """Generate a completion report for a task"""
        status = self.inspector.get_status()
        current_sha = self.persistence.get_current_commit_sha()
        
        report = {
            "task_id": task_id,
            "repository": status.repository,
            "branch": status.current_branch,
            "remote": status.remote,
            "is_clean": status.is_clean,
            "commit_sha": current_sha,
            "has_uncommitted_changes": status.has_uncommitted_changes,
            "ahead_count": status.ahead_count,
            "behind_count": status.behind_count,
            "publication_status": None,
            "remote_verified": False,
            "can_complete": False,
            "reason": "",
        }
        
        if self.publisher:
            pub_status = self.publisher.get_publication_status()
            report["publication_status"] = pub_status.value
            
            if current_sha:
                report["remote_verified"] = self.publisher.verify_remote_commit(current_sha)
        
        can_complete, reason, _ = self.can_complete_task(task_id, current_sha)
        report["can_complete"] = can_complete
        report["reason"] = reason
        
        return report
