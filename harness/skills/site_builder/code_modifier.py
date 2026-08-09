"""
Code Modifier - Safe code modification with diff analysis
"""
import difflib
from typing import Dict, List, Optional, Any

from .models import (
    CodeChange,
    FileOperation,
    DiffResult,
)


class CodeModifier:
    """Safely modifies code with diff analysis and validation"""
    
    def __init__(self):
        self.changes: List[CodeChange] = []
        self.diffs: List[DiffResult] = []
    
    def create_diff(self, file_path: str, old_content: str, 
                   new_content: str) -> DiffResult:
        """Create a diff between old and new content"""
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
        ))
        
        additions = 0
        deletions = 0
        changes = []
        
        for line in diff[2:]:  # Skip header lines
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
                changes.append({"type": "add", "content": line.rstrip()})
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
                changes.append({"type": "delete", "content": line.rstrip()})
        
        # Analyze risk level
        risk_level = "LOW"
        warnings = []
        is_safe = True
        
        # High deletion ratio indicates potential danger
        if old_content and deletions > len(old_content.splitlines()) * 0.5:
            risk_level = "HIGH"
            warnings.append("Large deletion detected - more than 50% of content removed")
            is_safe = False
        
        # Check for dangerous patterns
        dangerous_patterns = [
            "rm -rf",
            "DROP TABLE",
            "DELETE FROM",
            "process.exit",
            "eval(",
            "exec(",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in new_content:
                risk_level = "HIGH"
                warnings.append(f"Dangerous pattern detected: {pattern}")
                is_safe = False
        
        # Check for import removals
        if old_content:
            old_imports = [l for l in old_content.splitlines() if l.startswith('import ')]
            new_imports = [l for l in new_content.splitlines() if l.startswith('import ')]
            
            removed_imports = set(old_imports) - set(new_imports)
            if removed_imports:
                warnings.append(f"Imports removed: {len(removed_imports)}")
                if len(removed_imports) > 5:
                    risk_level = "MEDIUM" if risk_level == "LOW" else risk_level
        
        diff_result = DiffResult(
            file=file_path,
            changes=changes,
            additions=additions,
            deletions=deletions,
            is_safe=is_safe,
            risk_level=risk_level,
            warnings=warnings,
        )
        
        self.diffs.append(diff_result)
        return diff_result
    
    def analyze_diff_safety(self, diff_result: DiffResult, 
                           threshold: str = "MEDIUM") -> bool:
        """Analyze if a diff is safe to apply based on threshold"""
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        threshold_value = risk_order.get(threshold, 1)
        diff_risk = risk_order.get(diff_result.risk_level, 0)
        
        return diff_risk <= threshold_value
    
    def modify_code(self, file_path: str, old_content: str, new_content: str,
                   reason: str = "") -> tuple[CodeChange, DiffResult]:
        """Modify code with diff analysis"""
        # Create diff first
        diff_result = self.create_diff(file_path, old_content, new_content)
        
        # Create change record
        change = CodeChange(
            file=file_path,
            operation=FileOperation.MODIFY,
            reason=reason,
            before=old_content,
            after=new_content,
            risk=diff_result.risk_level,
        )
        
        self.changes.append(change)
        
        return change, diff_result
    
    def insert_code(self, file_path: str, content: str, 
                   search_pattern: str, position: str = "after",
                   original_content: str = "") -> tuple[CodeChange, DiffResult]:
        """Insert code at a specific location"""
        if not original_content:
            raise ValueError("original_content is required for insert operation")
        
        lines = original_content.splitlines()
        insert_index = -1
        
        for i, line in enumerate(lines):
            if search_pattern in line:
                insert_index = i + 1 if position == "after" else i
                break
        
        if insert_index == -1:
            # Pattern not found, append at end
            insert_index = len(lines)
        
        # Insert the new content lines
        new_lines = content.splitlines()
        for i, line in enumerate(new_lines):
            lines.insert(insert_index + i, line)
        
        new_content = "\n".join(lines)
        
        return self.modify_code(file_path, original_content, new_content,
                               f"Insert code {position} '{search_pattern}'")
    
    def replace_code_block(self, file_path: str, search_pattern: str,
                          replacement: str, original_content: str = "") -> tuple[CodeChange, DiffResult]:
        """Replace a code block matching a pattern"""
        if not original_content:
            raise ValueError("original_content is required for replace operation")
        
        import re
        new_content = re.sub(search_pattern, replacement, original_content)
        
        if new_content == original_content:
            raise ValueError(f"Pattern '{search_pattern}' not found in content")
        
        return self.modify_code(file_path, original_content, new_content,
                               f"Replace pattern '{search_pattern}'")
    
    def remove_code_block(self, file_path: str, search_pattern: str,
                         original_content: str = "") -> tuple[CodeChange, DiffResult]:
        """Remove a code block matching a pattern"""
        if not original_content:
            raise ValueError("original_content is required for remove operation")
        
        import re
        new_content = re.sub(search_pattern, "", original_content)
        
        if new_content == original_content:
            raise ValueError(f"Pattern '{search_pattern}' not found in content")
        
        return self.modify_code(file_path, original_content, new_content,
                               f"Remove pattern '{search_pattern}'")
    
    def get_all_changes(self) -> List[CodeChange]:
        """Get all recorded changes"""
        return self.changes
    
    def get_all_diffs(self) -> List[DiffResult]:
        """Get all recorded diffs"""
        return self.diffs
    
    def clear_history(self):
        """Clear change and diff history"""
        self.changes.clear()
        self.diffs.clear()
    
    def validate_syntax(self, content: str, language: str = "typescript") -> tuple[bool, List[str]]:
        """Basic syntax validation"""
        errors = []
        
        if language in ["typescript", "javascript", "tsx", "jsx"]:
            # Check for basic syntax issues
            open_braces = content.count('{') - content.count('}')
            open_parens = content.count('(') - content.count(')')
            open_brackets = content.count('[') - content.count(']')
            
            if open_braces != 0:
                errors.append(f"Unbalanced braces: {'missing }' if open_braces > 0 else 'extra }'}")
            if open_parens != 0:
                errors.append(f"Unbalanced parentheses: {'missing )' if open_parens > 0 else 'extra )'}")
            if open_brackets != 0:
                errors.append(f"Unbalanced brackets: {'missing ]' if open_brackets > 0 else 'extra ]'}")
            
            # Check for unclosed strings (basic check)
            single_quotes = content.count("'") - content.count("\\'")
            double_quotes = content.count('"') - content.count('\\"')
            
            if single_quotes % 2 != 0:
                errors.append("Unclosed single quote string detected")
            if double_quotes % 2 != 0:
                errors.append("Unclosed double quote string detected")
        
        return len(errors) == 0, errors
    
    def get_diff_summary(self, diff_result: DiffResult) -> str:
        """Get a human-readable summary of a diff"""
        summary = f"File: {diff_result.file}\n"
        summary += f"Additions: {diff_result.additions}\n"
        summary += f"Deletions: {diff_result.deletions}\n"
        summary += f"Risk Level: {diff_result.risk_level}\n"
        summary += f"Safe to Apply: {diff_result.is_safe}\n"
        
        if diff_result.warnings:
            summary += "Warnings:\n"
            for warning in diff_result.warnings:
                summary += f"  - {warning}\n"
        
        return summary
