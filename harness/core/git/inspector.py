"""
Git Inspector - Inspects Git repository state
"""
import subprocess
import os
from typing import Optional, List, Tuple
from harness.core.git.models import GitStatus


class GitInspector:
    """Inspects Git repository state and provides status information"""
    
    SENSITIVE_PATTERNS = [
        ".env",
        ".env.*",
        "*.pem",
        "*.key",
        "*_rsa",
        "*_dsa",
        "*_ecdsa",
        "*_ed25519",
        "*.p12",
        "*.pfx",
        "credentials",
        "secrets",
        "*password*",
        "*token*",
        "*api_key*",
        "*apikey*",
        "*secret*",
    ]
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
    
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
    
    def is_repository(self) -> bool:
        """Check if current directory is a Git repository"""
        success, _, _ = self._run_git(["rev-parse", "--git-dir"])
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name"""
        success, stdout, _ = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        if success and stdout:
            return stdout
        return None
    
    def get_remote(self) -> Optional[str]:
        """Get the default remote URL"""
        success, stdout, _ = self._run_git(["remote", "get-url", "origin"])
        if success and stdout:
            return stdout
        return None
    
    def get_uncommitted_changes(self) -> List[str]:
        """Get list of files with uncommitted changes (not staged)"""
        success, stdout, _ = self._run_git(["diff", "--name-only"])
        if success and stdout:
            return [f.strip() for f in stdout.split("\n") if f.strip()]
        return []
    
    def get_staged_changes(self) -> List[str]:
        """Get list of staged files"""
        success, stdout, _ = self._run_git(["diff", "--cached", "--name-only"])
        if success and stdout:
            return [f.strip() for f in stdout.split("\n") if f.strip()]
        return []
    
    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files"""
        success, stdout, _ = self._run_git(["ls-files", "--others", "--exclude-standard"])
        if success and stdout:
            return [f.strip() for f in stdout.split("\n") if f.strip()]
        return []
    
    def get_last_commit(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Get last commit info (sha, message, timestamp)"""
        success, stdout, _ = self._run_git([
            "log", "-1", "--format=%H|%s|%ai"
        ])
        if success and stdout:
            parts = stdout.split("|")
            if len(parts) >= 3:
                return parts[0], parts[1], parts[2]
        return None, None, None
    
    def get_ahead_behind(self) -> Tuple[int, int]:
        """Get ahead/behind count compared to remote"""
        branch = self.get_current_branch()
        if not branch:
            return 0, 0
        
        success, stdout, _ = self._run_git([
            "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD"
        ])
        if success and stdout:
            parts = stdout.split()
            if len(parts) >= 2:
                try:
                    behind = int(parts[0])
                    ahead = int(parts[1])
                    return ahead, behind
                except ValueError:
                    pass
        return 0, 0
    
    def contains_sensitive_files(self, files: List[str]) -> List[str]:
        """Check if any files match sensitive patterns"""
        sensitive = []
        for file_path in files:
            filename = os.path.basename(file_path).lower()
            filepath_lower = file_path.lower()
            
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern.startswith("*") and pattern.endswith("*"):
                    # Contains wildcard pattern
                    if pattern[1:-1] in filepath_lower:
                        sensitive.append(file_path)
                        break
                elif pattern.endswith(".*"):
                    # Extension pattern like .env.*
                    prefix = pattern[:-2]
                    if filename.startswith(prefix):
                        sensitive.append(file_path)
                        break
                elif "*" in pattern:
                    # Simple glob pattern
                    import fnmatch
                    if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(filepath_lower, pattern):
                        sensitive.append(file_path)
                        break
                else:
                    # Exact match
                    if pattern in filepath_lower or pattern in filename:
                        sensitive.append(file_path)
                        break
        
        return sensitive
    
    def get_status(self) -> GitStatus:
        """Get comprehensive Git status"""
        if not self.is_repository():
            return GitStatus(is_clean=False)
        
        uncommitted = self.get_uncommitted_changes()
        staged = self.get_staged_changes()
        untracked = self.get_untracked_files()
        last_commit_sha, last_commit_msg, last_commit_ts = self.get_last_commit()
        ahead, behind = self.get_ahead_behind()
        
        has_changes = bool(uncommitted or staged or untracked)
        
        return GitStatus(
            repository=self.repo_path,
            current_branch=self.get_current_branch(),
            remote=self.get_remote(),
            has_uncommitted_changes=len(uncommitted) > 0,
            has_staged_changes=len(staged) > 0,
            has_untracked_files=len(untracked) > 0,
            uncommitted_files=uncommitted,
            staged_files=staged,
            untracked_files=untracked,
            last_commit_message=last_commit_msg,
            last_commit_sha=last_commit_sha,
            last_commit_timestamp=last_commit_ts,
            ahead_count=ahead,
            behind_count=behind,
            is_clean=not has_changes,
        )
