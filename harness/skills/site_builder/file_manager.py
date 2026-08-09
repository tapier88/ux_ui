"""
File Manager - Handles file operations and ownership management
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import (
    FileOperation,
    FileOwnership,
    CodeChange,
)


class FileManager:
    """Manages file operations with ownership classification"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.file_ownership: Dict[str, FileOwnership] = {}
        self.changes: List[CodeChange] = []
    
    def classify_file(self, file_path: str, ownership: FileOwnership, reason: str = ""):
        """Classify a file's ownership status"""
        self.file_ownership[file_path] = ownership
    
    def get_ownership(self, file_path: str) -> FileOwnership:
        """Get the ownership classification for a file"""
        return self.file_ownership.get(file_path, FileOwnership.PRESERVE)
    
    def can_modify(self, file_path: str) -> bool:
        """Check if a file can be modified"""
        ownership = self.get_ownership(file_path)
        return ownership in [FileOwnership.MODIFY, FileOwnership.REPLACE, FileOwnership.CREATE]
    
    def create_file(self, file_path: str, content: str, reason: str = "") -> CodeChange:
        """Create a new file"""
        full_path = self.project_path / file_path
        
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(full_path, 'w') as f:
            f.write(content)
        
        change = CodeChange(
            file=file_path,
            operation=FileOperation.CREATE,
            reason=reason,
            after=content,
            risk="LOW"
        )
        self.changes.append(change)
        self.classify_file(file_path, FileOwnership.CREATE)
        
        return change
    
    def modify_file(self, file_path: str, old_content: str, new_content: str, 
                    reason: str = "") -> CodeChange:
        """Modify an existing file"""
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return self.create_file(file_path, new_content, reason)
        
        # Write new content
        with open(full_path, 'w') as f:
            f.write(new_content)
        
        change = CodeChange(
            file=file_path,
            operation=FileOperation.MODIFY,
            reason=reason,
            before=old_content,
            after=new_content,
            risk="MEDIUM"
        )
        self.changes.append(change)
        self.classify_file(file_path, FileOwnership.MODIFY)
        
        return change
    
    def delete_file(self, file_path: str, reason: str = "") -> CodeChange:
        """Delete a file"""
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            change = CodeChange(
                file=file_path,
                operation=FileOperation.DELETE,
                reason=f"File does not exist: {reason}",
                risk="LOW"
            )
            self.changes.append(change)
            return change
        
        # Read content before deletion for rollback
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Delete the file
        full_path.unlink()
        
        change = CodeChange(
            file=file_path,
            operation=FileOperation.DELETE,
            reason=reason,
            before=content,
            risk="HIGH"
        )
        self.changes.append(change)
        self.classify_file(file_path, FileOwnership.REMOVE)
        
        return change
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read a file's content"""
        full_path = self.project_path / file_path
        
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except IOError:
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists"""
        full_path = self.project_path / file_path
        return full_path.exists()
    
    def get_all_changes(self) -> List[CodeChange]:
        """Get all recorded changes"""
        return self.changes
    
    def clear_changes(self):
        """Clear the changes log"""
        self.changes.clear()
    
    def validate_path(self, file_path: str) -> bool:
        """Validate that a path is safe (no path traversal)"""
        # Normalize the path
        normalized = os.path.normpath(file_path)
        
        # Check for path traversal attempts
        if normalized.startswith('..') or normalized.startswith('/'):
            return False
        
        # Resolve to absolute path and ensure it's within project
        try:
            resolved = (self.project_path / file_path).resolve()
            project_resolved = self.project_path.resolve()
            
            # Ensure the resolved path starts with the project path
            return str(resolved).startswith(str(project_resolved))
        except (ValueError, OSError):
            return False
    
    def safe_path(self, file_path: str) -> Optional[Path]:
        """Get a safe path or None if invalid"""
        if not self.validate_path(file_path):
            return None
        
        return self.project_path / file_path
    
    def copy_file(self, source_path: str, dest_path: str, reason: str = "") -> CodeChange:
        """Copy a file from source to destination"""
        source_full = self.project_path / source_path
        dest_full = self.project_path / dest_path
        
        if not source_full.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Ensure parent directory exists
        dest_full.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_full, dest_full)
        
        change = CodeChange(
            file=dest_path,
            operation=FileOperation.CREATE,
            reason=f"Copied from {source_path}: {reason}",
            risk="LOW"
        )
        self.changes.append(change)
        
        return change
    
    def move_file(self, source_path: str, dest_path: str, reason: str = "") -> tuple[CodeChange, CodeChange]:
        """Move a file from source to destination"""
        source_full = self.project_path / source_path
        dest_full = self.project_path / dest_path
        
        if not source_full.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Ensure parent directory exists
        dest_full.parent.mkdir(parents=True, exist_ok=True)
        
        # Read source content for rollback
        with open(source_full, 'r') as f:
            source_content = f.read()
        
        # Move the file
        shutil.move(str(source_full), str(dest_full))
        
        delete_change = CodeChange(
            file=source_path,
            operation=FileOperation.DELETE,
            reason=f"Moved to {dest_path}: {reason}",
            before=source_content,
            risk="MEDIUM"
        )
        
        create_change = CodeChange(
            file=dest_path,
            operation=FileOperation.CREATE,
            reason=f"Moved from {source_path}: {reason}",
            risk="MEDIUM"
        )
        
        self.changes.extend([delete_change, create_change])
        
        return delete_change, create_change
