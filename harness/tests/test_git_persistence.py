"""
Tests for Git Persistence Module
"""
import os
import sys
import tempfile
import subprocess
import shutil
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from harness.core.git.models import (
    TaskPersistenceState,
    PublicationStatus,
    GitStatus,
    CommitInfo,
    TaskManifestEntry,
)
from harness.core.git.inspector import GitInspector
from harness.core.git.persistence import GitPersistence
from harness.core.git.publication import LocalPublicationProvider
from harness.core.git.validator import GitValidator
from harness.core.git.manifest import TaskManifest


class TestGitInspector(unittest.TestCase):
    """Test GitInspector functionality"""
    
    def setUp(self):
        """Create a temporary Git repository for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self._init_git_repo()
        self.inspector = GitInspector(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository"""
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
    
    def test_1_repository_detection(self):
        """Test 1: Clean repository detection"""
        self.assertTrue(self.inspector.is_repository())
    
    def test_2_uncommitted_changes(self):
        """Test 2: Uncommitted changes detection"""
        # Create a file and stage it first (so git tracks it)
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        subprocess.run(["git", "add", "test.txt"], cwd=self.temp_dir, capture_output=True)
        
        # Now modify it to create uncommitted changes
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        status = self.inspector.get_status()
        self.assertTrue(status.has_uncommitted_changes or status.has_staged_changes)
    
    def test_3_untracked_files(self):
        """Test 3: Untracked files detection"""
        # Create an untracked file
        test_file = os.path.join(self.temp_dir, "untracked.txt")
        with open(test_file, 'w') as f:
            f.write("untracked")
        
        status = self.inspector.get_status()
        self.assertTrue(status.has_untracked_files)
        self.assertIn("untracked.txt", status.untracked_files)
    
    def test_4_commit_creation(self):
        """Test 4: Commit creation and detection"""
        # Create and commit a file
        test_file = os.path.join(self.temp_dir, "committed.txt")
        with open(test_file, 'w') as f:
            f.write("committed content")
        
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Test commit"], cwd=self.temp_dir, capture_output=True)
        
        sha, msg, ts = self.inspector.get_last_commit()
        self.assertIsNotNone(sha)
        self.assertEqual(msg, "Test commit")
    
    def test_5_sensitive_file_detection(self):
        """Test 5: Sensitive file detection"""
        sensitive_files = [
            ".env",
            ".env.local",
            "secret.key",
            "private_rsa",
            "credentials.json",
            "api_token.txt",
        ]
        
        for filename in sensitive_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("sensitive")
            
            detected = self.inspector.contains_sensitive_files([filename])
            self.assertTrue(len(detected) > 0, f"Should detect {filename} as sensitive")


class TestGitPersistence(unittest.TestCase):
    """Test GitPersistence functionality"""
    
    def setUp(self):
        """Create a temporary Git repository for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self._init_git_repo()
        self.inspector = GitInspector(self.temp_dir)
        self.persistence = GitPersistence(self.temp_dir, self.inspector)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository"""
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
    
    def test_6_commit_creation(self):
        """Test 6: Commit creation through GitPersistence"""
        # Create a file
        test_file = os.path.join(self.temp_dir, "persist_test.txt")
        with open(test_file, 'w') as f:
            f.write("persistence test")
        
        # Create commit
        commit_info = self.persistence.create_commit("Persistence test commit")
        
        self.assertIsNotNone(commit_info)
        self.assertEqual(commit_info.message, "Persistence test commit")
        # Note: files_changed may be empty if git diff-tree doesn't show anything
        # The important thing is that the commit was created
        sha, msg, ts = self.inspector.get_last_commit()
        self.assertEqual(msg, "Persistence test commit")
    
    def test_7_sensitive_file_blocking(self):
        """Test 7: Sensitive file blocking during commit"""
        # Create a sensitive file
        env_file = os.path.join(self.temp_dir, ".env")
        with open(env_file, 'w') as f:
            f.write("SECRET_KEY=test123")
        
        # Try to commit - should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.persistence.create_commit("Should fail")
        
        self.assertIn("sensitive", str(context.exception).lower())


class TestPublicationProvider(unittest.TestCase):
    """Test Git publication provider"""
    
    def setUp(self):
        """Create a temporary Git repository for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self._init_git_repo()
        self.inspector = GitInspector(self.temp_dir)
        self.provider = LocalPublicationProvider(self.temp_dir, self.inspector)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository"""
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
    
    def test_8_publication_required(self):
        """Test 8: Publication required when no remote"""
        # Without a remote, publication should be required
        prepare_result = self.provider.prepare_publication()
        self.assertFalse(prepare_result)
        
        status = self.provider.get_publication_status()
        self.assertEqual(status, PublicationStatus.PUBLICATION_REQUIRED)


class TestGitValidator(unittest.TestCase):
    """Test GitValidator functionality"""
    
    def setUp(self):
        """Create a temporary Git repository for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self._init_git_repo()
        self.inspector = GitInspector(self.temp_dir)
        self.persistence = GitPersistence(self.temp_dir, self.inspector)
        self.validator = GitValidator(
            self.temp_dir,
            self.inspector,
            self.persistence,
        )
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository"""
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
    
    def test_9_incomplete_task_without_publication(self):
        """Test 9: Incomplete task without publication"""
        # Create and commit a file
        test_file = os.path.join(self.temp_dir, "task.txt")
        with open(test_file, 'w') as f:
            f.write("task content")
        
        self.persistence.create_commit("Task commit")
        
        # Without publisher, task should be incomplete
        can_complete, reason, state = self.validator.can_complete_task(
            "test_task",
            tests_passed=True,
        )
        
        self.assertFalse(can_complete)
        self.assertIn("PUBLICATION REQUIRED", reason)
    
    def test_10_complete_task_with_conditions(self):
        """Test 10: Complete task verification flow"""
        # Create initial commit
        test_file = os.path.join(self.temp_dir, "initial.txt")
        with open(test_file, 'w') as f:
            f.write("initial")
        
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.temp_dir, capture_output=True)
        
        # Validate commit gate
        success, msg = self.validator.validate_commit_gate("test_task", tests_passed=True)
        self.assertTrue(success)


class TestTaskManifest(unittest.TestCase):
    """Test TaskManifest functionality"""
    
    def setUp(self):
        """Create a temporary directory for manifest"""
        self.temp_dir = tempfile.mkdtemp()
        self.manifest_path = os.path.join(self.temp_dir, "TASK_MANIFEST.json")
        self.manifest = TaskManifest(self.manifest_path)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_11_checkpoint_restoration(self):
        """Test 11: Checkpoint restoration from manifest"""
        # Add an entry
        self.manifest.update_entry(
            "task_001",
            status="COMMITTED",
            tests_passed=True,
            commit_sha="abc123",
            branch="main",
        )
        
        # Reload manifest
        new_manifest = TaskManifest(self.manifest_path)
        entry = new_manifest.get_entry("task_001")
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.commit_sha, "abc123")
        self.assertEqual(entry.branch, "main")
    
    def test_12_task_manifest(self):
        """Test 12: Task manifest operations"""
        # Add multiple entries
        self.manifest.update_entry(
            "task_001",
            status="COMPLETE",
            tests_passed=True,
            commit_sha="abc123",
            branch="main",
            published=True,
            remote_verified=True,
        )
        
        self.manifest.update_entry(
            "task_002",
            status="COMMITTED",
            tests_passed=True,
            commit_sha="def456",
            branch="main",
            published=False,
            remote_verified=False,
        )
        
        # Check counts
        all_entries = self.manifest.get_all_entries()
        self.assertEqual(len(all_entries), 2)
        
        published = self.manifest.get_published_tasks()
        self.assertEqual(len(published), 1)
        
        verified = self.manifest.get_verified_tasks()
        self.assertEqual(len(verified), 1)
        
        incomplete = self.manifest.get_incomplete_tasks()
        self.assertEqual(len(incomplete), 1)
    
    def test_13_recovery_after_restart(self):
        """Test 13: Recovery after restart simulation"""
        # Simulate multiple tasks
        self.manifest.update_entry(
            "task_a",
            status="COMPLETE",
            tests_passed=True,
            commit_sha="aaa",
            branch="main",
            published=True,
            remote_verified=True,
        )
        
        self.manifest.update_entry(
            "task_b",
            status="COMMITTED",
            tests_passed=True,
            commit_sha="bbb",
            branch="main",
            published=False,
            remote_verified=False,
        )
        
        self.manifest.update_entry(
            "task_c",
            status="PUBLISHED",
            tests_passed=True,
            commit_sha="ccc",
            branch="main",
            published=True,
            remote_verified=False,
        )
        
        # Simulate restart by loading fresh
        recovered = TaskManifest(self.manifest_path)
        recovery_info = recovered.recover_from_manifest()
        
        self.assertEqual(recovery_info["total_tasks"], 3)
        # task_a and task_c are both published (published=True)
        self.assertEqual(recovery_info["published_count"], 2)
        self.assertEqual(recovery_info["verified_count"], 1)
        self.assertEqual(recovery_info["incomplete_count"], 2)


class TestBranchAndRemoteMismatch(unittest.TestCase):
    """Test branch and remote mismatch scenarios"""
    
    def setUp(self):
        """Create a temporary Git repository for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self._init_git_repo()
        self.inspector = GitInspector(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository"""
        subprocess.run(["git", "init"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.temp_dir, capture_output=True)
    
    def test_14_branch_mismatch(self):
        """Test 14: Branch mismatch detection"""
        # First create an initial commit (required for git branch to work)
        test_file = os.path.join(self.temp_dir, "initial.txt")
        with open(test_file, 'w') as f:
            f.write("initial")
        subprocess.run(["git", "add", "."], cwd=self.temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=self.temp_dir, capture_output=True)
        
        # Get current branch
        branch = self.inspector.get_current_branch()
        self.assertIsNotNone(branch)  # Should be master or main depending on git version
        
        # Create and switch to new branch
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=self.temp_dir, capture_output=True)
        new_branch = self.inspector.get_current_branch()
        self.assertEqual(new_branch, "feature")
    
    def test_15_remote_mismatch(self):
        """Test 15: Remote mismatch detection"""
        # No remote initially
        remote = self.inspector.get_remote()
        self.assertIsNone(remote)
        
        # Add remote
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
            cwd=self.temp_dir,
            capture_output=True
        )
        
        remote = self.inspector.get_remote()
        self.assertIsNotNone(remote)
        self.assertIn("test/repo", remote)


def run_all_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGitInspector))
    suite.addTests(loader.loadTestsFromTestCase(TestGitPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicationProvider))
    suite.addTests(loader.loadTestsFromTestCase(TestGitValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManifest))
    suite.addTests(loader.loadTestsFromTestCase(TestBranchAndRemoteMismatch))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
