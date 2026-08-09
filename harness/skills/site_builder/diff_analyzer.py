"""
Diff Analyzer - Diff safety analysis
"""
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import (
    DiffResult,
)


class DiffAnalyzer:
    """Analyzes code diffs for safety and risk"""
    
    def __init__(self):
        self.analysis_history: List[DiffResult] = []
    
    def analyze_diff(self, file_path: str, old_content: str, 
                    new_content: str) -> DiffResult:
        """Analyze a diff for safety and risk"""
        old_lines = old_content.splitlines(keepends=True) if old_content else []
        new_lines = new_content.splitlines(keepends=True) if new_content else []
        
        # Generate unified diff
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
        
        # Analyze risk factors
        risk_level = "LOW"
        warnings = []
        is_safe = True
        
        # Factor 1: Deletion ratio
        total_old_lines = len(old_lines)
        if total_old_lines > 0 and deletions > total_old_lines * 0.5:
            risk_level = "HIGH"
            warnings.append(f"Large deletion: {deletions}/{total_old_lines} lines removed")
            is_safe = False
        
        # Factor 2: Addition ratio (sudden large additions)
        total_new_lines = len(new_lines)
        if total_new_lines > 0 and additions > total_new_lines * 0.8:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            warnings.append(f"Large addition: {additions} lines added")
        
        # Factor 3: Dangerous patterns
        dangerous_patterns = [
            ("rm -rf", "Shell command: recursive delete"),
            ("DROP TABLE", "SQL command: drop table"),
            ("DELETE FROM", "SQL command: delete"),
            ("process.exit", "Process termination"),
            ("eval(", "Code evaluation"),
            ("exec(", "Code execution"),
            ("child_process", "Child process execution"),
            ("fs.unlink", "File deletion"),
            ("fs.rmdir", "Directory removal"),
        ]
        
        for pattern, description in dangerous_patterns:
            if pattern in new_content:
                risk_level = "HIGH"
                warnings.append(f"Dangerous pattern detected: {description}")
                is_safe = False
        
        # Factor 4: Import changes
        old_imports = set(l for l in old_content.splitlines() if l.strip().startswith('import '))
        new_imports = set(l for l in new_content.splitlines() if l.strip().startswith('import '))
        
        removed_imports = old_imports - new_imports
        added_imports = new_imports - old_imports
        
        if len(removed_imports) > 5:
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            warnings.append(f"Multiple imports removed: {len(removed_imports)}")
        
        if added_imports:
            # Check for suspicious imports
            suspicious = ["child_process", "fs", "net", "dgram", "dns"]
            for imp in added_imports:
                for sus in suspicious:
                    if sus in imp.lower():
                        if risk_level == "LOW":
                            risk_level = "MEDIUM"
                        warnings.append(f"Potentially risky import: {imp}")
        
        # Factor 5: File type considerations
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.env', '.config', '.conf']:
            risk_level = "HIGH" if risk_level != "HIGH" else risk_level
            warnings.append("Configuration file modified")
        
        if file_ext in ['.json'] and 'package' in file_path.lower():
            risk_level = "MEDIUM" if risk_level == "LOW" else risk_level
            warnings.append("Package configuration modified")
        
        # Factor 6: Syntax balance check
        syntax_warnings = self._check_syntax_balance(new_content, file_ext)
        if syntax_warnings:
            warnings.extend(syntax_warnings)
            if risk_level == "LOW":
                risk_level = "MEDIUM"
            is_safe = False
        
        result = DiffResult(
            file=file_path,
            changes=changes[:100],  # Limit changes for performance
            additions=additions,
            deletions=deletions,
            is_safe=is_safe,
            risk_level=risk_level,
            warnings=warnings,
        )
        
        self.analysis_history.append(result)
        return result
    
    def _check_syntax_balance(self, content: str, file_ext: str) -> List[str]:
        """Check for basic syntax balance issues"""
        warnings = []
        
        if file_ext in ['.ts', '.tsx', '.js', '.jsx']:
            # Check braces
            open_braces = content.count('{') - content.count('}')
            if open_braces != 0:
                warnings.append(f"Unbalanced braces: {'missing }' if open_braces > 0 else 'extra }'}")
            
            # Check parentheses
            open_parens = content.count('(') - content.count(')')
            if abs(open_parens) > 2:  # Allow small imbalances
                warnings.append(f"Unbalanced parentheses: {'missing )' if open_parens > 0 else 'extra )'}")
            
            # Check brackets
            open_brackets = content.count('[') - content.count(']')
            if open_brackets != 0:
                warnings.append(f"Unbalanced brackets: {'missing ]' if open_brackets > 0 else 'extra ]'}")
        
        elif file_ext in ['.html', '.htm', '.tsx', '.jsx']:
            # Basic HTML tag balance (simplified)
            open_tags = content.count('<div') - content.count('</div>')
            if open_tags > 2:
                warnings.append("Possible unbalanced div tags")
        
        return warnings
    
    def compare_diffs(self, diff1: DiffResult, diff2: DiffResult) -> Dict[str, Any]:
        """Compare two diffs"""
        return {
            "file1": diff1.file,
            "file2": diff2.file,
            "diff1_additions": diff1.additions,
            "diff2_additions": diff2.additions,
            "diff1_deletions": diff1.deletions,
            "diff2_deletions": diff2.deletions,
            "diff1_risk": diff1.risk_level,
            "diff2_risk": diff2.risk_level,
            "both_safe": diff1.is_safe and diff2.is_safe,
        }
    
    def get_risky_files(self, threshold: str = "MEDIUM") -> List[DiffResult]:
        """Get all diffs with risk level at or above threshold"""
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        threshold_value = risk_order.get(threshold, 1)
        
        return [
            d for d in self.analysis_history
            if risk_order.get(d.risk_level, 0) >= threshold_value
        ]
    
    def get_all_results(self) -> List[DiffResult]:
        """Get all diff analysis results"""
        return self.analysis_history
    
    def clear_history(self):
        """Clear analysis history"""
        self.analysis_history.clear()
    
    def generate_safety_report(self) -> Dict[str, Any]:
        """Generate a safety report for all analyzed diffs"""
        total = len(self.analysis_history)
        safe_count = sum(1 for d in self.analysis_history if d.is_safe)
        high_risk_count = sum(1 for d in self.analysis_history if d.risk_level == "HIGH")
        
        return {
            "total_analyzed": total,
            "safe_count": safe_count,
            "unsafe_count": total - safe_count,
            "high_risk_count": high_risk_count,
            "safety_percentage": (safe_count / total * 100) if total > 0 else 100,
            "warnings_summary": self._summarize_warnings(),
        }
    
    def _summarize_warnings(self) -> Dict[str, int]:
        """Summarize warning types"""
        warning_counts = {}
        
        for diff in self.analysis_history:
            for warning in diff.warnings:
                # Categorize warning
                if "deletion" in warning.lower():
                    warning_counts["deletions"] = warning_counts.get("deletions", 0) + 1
                elif "dangerous" in warning.lower():
                    warning_counts["dangerous_patterns"] = warning_counts.get("dangerous_patterns", 0) + 1
                elif "import" in warning.lower():
                    warning_counts["imports"] = warning_counts.get("imports", 0) + 1
                elif "unbalanced" in warning.lower():
                    warning_counts["syntax_issues"] = warning_counts.get("syntax_issues", 0) + 1
                else:
                    warning_counts["other"] = warning_counts.get("other", 0) + 1
        
        return warning_counts
