"""
Rollback - Checkpoint and rollback functionality
"""
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import (
    CheckpointInfo,
    RollbackResult,
)


class RollbackManager:
    """Manages checkpoints and rollback operations"""
    
    def __init__(self, project_path: str, task_id: str):
        self.project_path = Path(project_path)
        self.task_id = task_id
        self.checkpoints: Dict[str, CheckpointInfo] = {}
        self.checkpoint_dir = self.project_path / ".harness" / "checkpoints" / task_id
        
    def create_checkpoint(self, checkpoint_id: str, description: str,
                         files_to_snapshot: Optional[List[str]] = None) -> CheckpointInfo:
        """Create a checkpoint of the current state"""
        # Ensure checkpoint directory exists
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect file snapshots
        files_snapshot = {}
        
        if files_to_snapshot:
            for file_path in files_to_snapshot:
                full_path = self.project_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r') as f:
                            files_snapshot[file_path] = f.read()
                    except Exception:
                        pass
        else:
            # Snapshot all tracked files (limited)
            for ext in ['*.py', '*.ts', '*.tsx', '*.js', '*.jsx', '*.css', '*.json']:
                for f in self.project_path.rglob(ext):
                    if '.harness' not in str(f) and 'node_modules' not in str(f):
                        try:
                            rel_path = str(f.relative_to(self.project_path))
                            with open(f, 'r') as file:
                                files_snapshot[rel_path] = file.read()
                        except Exception:
                            pass
        
        # Create checkpoint info
        from harness.core.time import utc_now_iso
        checkpoint = CheckpointInfo(
            checkpoint_id=checkpoint_id,
            task_id=self.task_id,
            timestamp=utc_now_iso(),
            description=description,
            files_snapshot=files_snapshot,
        )
        
        # Save checkpoint to disk
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)
        
        self.checkpoints[checkpoint_id] = checkpoint
        
        return checkpoint
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointInfo]:
        """Get a specific checkpoint"""
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]
        
        # Try to load from disk
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r') as f:
                    data = json.load(f)
                
                checkpoint = CheckpointInfo(
                    checkpoint_id=data['checkpoint_id'],
                    task_id=data['task_id'],
                    timestamp=data['timestamp'],
                    description=data['description'],
                    files_snapshot=data.get('files_snapshot', {}),
                )
                
                self.checkpoints[checkpoint_id] = checkpoint
                return checkpoint
            except Exception:
                return None
        
        return None
    
    def get_last_checkpoint(self) -> Optional[CheckpointInfo]:
        """Get the most recent checkpoint"""
        if not self.checkpoints:
            # Load all checkpoints from disk
            if self.checkpoint_dir.exists():
                for f in self.checkpoint_dir.glob("*.json"):
                    try:
                        with open(f, 'r') as file:
                            data = json.load(file)
                        checkpoint_id = data['checkpoint_id']
                        self.checkpoints[checkpoint_id] = CheckpointInfo(
                            checkpoint_id=data['checkpoint_id'],
                            task_id=data['task_id'],
                            timestamp=data['timestamp'],
                            description=data['description'],
                            files_snapshot=data.get('files_snapshot', {}),
                        )
                    except Exception:
                        pass
        
        if not self.checkpoints:
            return None
        
        # Return the most recent by timestamp
        sorted_checkpoints = sorted(
            self.checkpoints.values(),
            key=lambda c: c.timestamp,
            reverse=True
        )
        
        return sorted_checkpoints[0]
    
    def rollback(self, checkpoint_id: Optional[str] = None) -> RollbackResult:
        """Rollback to a checkpoint"""
        if checkpoint_id is None:
            checkpoint = self.get_last_checkpoint()
            if not checkpoint:
                return RollbackResult(
                    success=False,
                    checkpoint_id="",
                    errors=["No checkpoint found to rollback to"],
                )
            checkpoint_id = checkpoint.checkpoint_id
        else:
            checkpoint = self.get_checkpoint(checkpoint_id)
            if not checkpoint:
                return RollbackResult(
                    success=False,
                    checkpoint_id=checkpoint_id,
                    errors=[f"Checkpoint not found: {checkpoint_id}"],
                )
        
        files_restored = []
        errors = []
        
        # Restore each file from the snapshot
        for file_path, content in checkpoint.files_snapshot.items():
            try:
                full_path = self.project_path / file_path
                
                # Ensure parent directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the content
                with open(full_path, 'w') as f:
                    f.write(content)
                
                files_restored.append(file_path)
            except Exception as e:
                errors.append(f"Failed to restore {file_path}: {str(e)}")
        
        success = len(errors) == 0
        
        result = RollbackResult(
            success=success,
            checkpoint_id=checkpoint_id,
            files_restored=files_restored,
            errors=errors,
        )
        
        return result
    
    def list_checkpoints(self) -> List[str]:
        """List all available checkpoint IDs"""
        checkpoint_ids = list(self.checkpoints.keys())
        
        # Also check disk
        if self.checkpoint_dir.exists():
            for f in self.checkpoint_dir.glob("*.json"):
                checkpoint_id = f.stem
                if checkpoint_id not in checkpoint_ids:
                    checkpoint_ids.append(checkpoint_id)
        
        return checkpoint_ids
    
    def clear_old_checkpoints(self, keep_count: int = 3):
        """Clear old checkpoints, keeping only the most recent ones"""
        all_checkpoints = self.list_checkpoints()
        
        if len(all_checkpoints) <= keep_count:
            return
        
        # Sort by timestamp and keep only recent ones
        sorted_ids = sorted(
            all_checkpoints,
            key=lambda cid: self.checkpoints.get(cid, CheckpointInfo(
                checkpoint_id=cid, task_id="", timestamp="", description=""
            )).timestamp,
            reverse=True
        )
        
        to_delete = sorted_ids[keep_count:]
        
        for checkpoint_id in to_delete:
            checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
            if checkpoint_path.exists():
                checkpoint_path.unlink()
            
            if checkpoint_id in self.checkpoints:
                del self.checkpoints[checkpoint_id]
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a specific checkpoint"""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        
        if checkpoint_path.exists():
            checkpoint_path.unlink()
        
        if checkpoint_id in self.checkpoints:
            del self.checkpoints[checkpoint_id]
        
        return True
    
    def cleanup(self):
        """Clean up all checkpoints"""
        if self.checkpoint_dir.exists():
            shutil.rmtree(self.checkpoint_dir)
        
        self.checkpoints.clear()
