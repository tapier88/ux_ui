"""
Validation - Validation pipeline for builds, syntax, types, accessibility, etc.
"""
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    ValidationResult,
    ValidationStatus,
    BuildError,
    ErrorType,
    ErrorSeverity,
)


class Validator:
    """Runs validation checks on the project"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: List[ValidationResult] = []
        self.errors: List[BuildError] = []
    
    def run_syntax_check(self, file_path: Optional[str] = None) -> ValidationResult:
        """Run syntax check on files"""
        errors = []
        warnings = []
        
        # For TypeScript/JavaScript projects
        ts_files = list(self.project_path.rglob("*.ts")) + \
                   list(self.project_path.rglob("*.tsx"))
        
        js_files = list(self.project_path.rglob("*.js")) + \
                   list(self.project_path.rglob("*.jsx"))
        
        all_files = ts_files + js_files
        
        if file_path:
            target = self.project_path / file_path
            if target.exists():
                all_files = [target]
            else:
                return ValidationResult(
                    validation_type="syntax",
                    status=ValidationStatus.FAIL,
                    message=f"File not found: {file_path}",
                    errors=[f"File not found: {file_path}"],
                )
        
        # Basic syntax validation (in real implementation, use ESLint/tsc)
        for f in all_files[:50]:  # Limit to 50 files
            try:
                with open(f, 'r') as file:
                    content = file.read()
                
                # Check for basic syntax issues
                open_braces = content.count('{') - content.count('}')
                open_parens = content.count('(') - content.count(')')
                
                if open_braces != 0:
                    errors.append(f"Unbalanced braces in {f.name}")
                if open_parens != 0:
                    warnings.append(f"Unbalanced parentheses in {f.name}")
                    
            except Exception as e:
                errors.append(f"Error reading {f.name}: {str(e)}")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="syntax",
            status=status,
            message="Syntax check completed" if status == ValidationStatus.PASS else "Syntax errors found",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def run_type_check(self) -> ValidationResult:
        """Run TypeScript type check"""
        errors = []
        warnings = []
        
        # Check if tsconfig.json exists
        tsconfig = self.project_path / "tsconfig.json"
        
        if not tsconfig.exists():
            return ValidationResult(
                validation_type="type",
                status=ValidationStatus.WARNING,
                message="No tsconfig.json found - skipping type check",
                warnings=["TypeScript configuration not found"],
            )
        
        # Try to run tsc --noEmit
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                # Parse TypeScript errors
                for line in result.stderr.split('\n'):
                    if line.strip():
                        errors.append(line.strip())
            else:
                for line in result.stdout.split('\n'):
                    if line.strip() and "error" in line.lower():
                        errors.append(line.strip())
                        
        except subprocess.TimeoutExpired:
            errors.append("Type check timed out")
        except FileNotFoundError:
            return ValidationResult(
                validation_type="type",
                status=ValidationStatus.WARNING,
                message="TypeScript not installed - skipping type check",
                warnings=["TypeScript not found"],
            )
        except Exception as e:
            errors.append(f"Type check failed: {str(e)}")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="type",
            status=status,
            message="Type check completed" if status == ValidationStatus.PASS else "Type errors found",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def run_lint(self) -> ValidationResult:
        """Run linting"""
        errors = []
        warnings = []
        
        # Check for ESLint config
        eslint_configs = [".eslintrc.js", ".eslintrc.json", ".eslintrc", 
                         "eslint.config.js", ".eslintrc.cjs"]
        has_eslint = any((self.project_path / c).exists() for c in eslint_configs)
        
        if not has_eslint:
            return ValidationResult(
                validation_type="lint",
                status=ValidationStatus.WARNING,
                message="No ESLint configuration found - skipping lint",
                warnings=["ESLint configuration not found"],
            )
        
        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--max-warnings", "0"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout + result.stderr
            
            for line in output.split('\n'):
                if line.strip():
                    if "error" in line.lower():
                        errors.append(line.strip())
                    elif "warning" in line.lower():
                        warnings.append(line.strip())
                        
        except subprocess.TimeoutExpired:
            errors.append("Lint timed out")
        except FileNotFoundError:
            return ValidationResult(
                validation_type="lint",
                status=ValidationStatus.WARNING,
                message="ESLint not installed - skipping lint",
                warnings=["ESLint not found"],
            )
        except Exception as e:
            errors.append(f"Lint failed: {str(e)}")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="lint",
            status=status,
            message="Lint completed" if status == ValidationStatus.PASS else "Lint errors found",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def run_build(self) -> ValidationResult:
        """Run the project build"""
        errors = []
        warnings = []
        
        # Detect build script from package.json
        import json
        package_json = self.project_path / "package.json"
        
        if not package_json.exists():
            return ValidationResult(
                validation_type="build",
                status=ValidationStatus.FAIL,
                message="No package.json found",
                errors=["package.json not found"],
            )
        
        with open(package_json, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        
        # Find build command
        build_cmd = None
        if "build" in scripts:
            build_cmd = scripts["build"]
        elif "dev" in scripts:
            # No build script, might be a dev-only project
            return ValidationResult(
                validation_type="build",
                status=ValidationStatus.WARNING,
                message="No build script found",
                warnings=["Project may not require build step"],
            )
        
        if not build_cmd:
            return ValidationResult(
                validation_type="build",
                status=ValidationStatus.FAIL,
                message="No build or dev script found",
                errors=["Cannot determine build command"],
            )
        
        # Detect package manager
        pm = "npm"
        if (self.project_path / "pnpm-lock.yaml").exists():
            pm = "pnpm"
        elif (self.project_path / "yarn.lock").exists():
            pm = "yarn"
        elif (self.project_path / "bun.lockb").exists():
            pm = "bun"
        
        try:
            result = subprocess.run(
                [pm, "run", "build"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                output = result.stderr or result.stdout
                for line in output.split('\n'):
                    if line.strip():
                        errors.append(line.strip())
                        
        except subprocess.TimeoutExpired:
            errors.append("Build timed out")
        except FileNotFoundError:
            errors.append(f"Package manager '{pm}' not found")
        except Exception as e:
            errors.append(f"Build failed: {str(e)}")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="build",
            status=status,
            message="Build completed successfully" if status == ValidationStatus.PASS else "Build failed",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def run_accessibility_check(self) -> ValidationResult:
        """Run accessibility validation (abstraction)"""
        errors = []
        warnings = []
        
        # This is an abstraction - real implementation would use:
        # - axe-core
        # - pa11y
        # - Lighthouse CI
        
        # Basic HTML structure checks
        html_files = list(self.project_path.rglob("*.html"))
        
        for f in html_files[:10]:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                
                # Check for lang attribute
                if '<html' in content and 'lang=' not in content:
                    warnings.append(f"Missing lang attribute in {f.name}")
                
                # Check for title
                if '<title>' not in content:
                    errors.append(f"Missing title in {f.name}")
                
            except Exception:
                pass
        
        # Check React components for accessibility patterns
        tsx_files = list(self.project_path.rglob("*.tsx"))
        
        for f in tsx_files[:20]:
            try:
                with open(f, 'r') as file:
                    content = file.read()
                
                # Check for img without alt
                if '<img' in content and 'alt=' not in content:
                    warnings.append(f"Image may be missing alt text in {f.name}")
                
                # Check for buttons without accessible names
                if '<button>' in content or '<button />' in content:
                    warnings.append(f"Button may need accessible name in {f.name}")
                
            except Exception:
                pass
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="accessibility",
            status=status,
            message="Accessibility check completed" if status == ValidationStatus.PASS else "Accessibility issues found",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def run_performance_check(self) -> ValidationResult:
        """Run performance validation (abstraction)"""
        errors = []
        warnings = []
        
        # This is an abstraction - real implementation would use:
        # - Lighthouse
        # - WebPageTest
        # - Bundle analyzer
        
        # Check for large assets
        public_dir = self.project_path / "public"
        if public_dir.exists():
            for f in public_dir.rglob("*"):
                if f.is_file():
                    size_mb = f.stat().st_size / (1024 * 1024)
                    if size_mb > 2:
                        warnings.append(f"Large asset: {f.name} ({size_mb:.2f} MB)")
        
        # Check for unoptimized images
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        for ext in image_extensions:
            for f in self.project_path.rglob(f"*{ext}"):
                if f.is_file():
                    size_mb = f.stat().st_size / (1024 * 1024)
                    if size_mb > 1:
                        warnings.append(f"Consider optimizing: {f.name} ({size_mb:.2f} MB)")
        
        status = ValidationStatus.PASS if not errors else ValidationStatus.FAIL
        
        result = ValidationResult(
            validation_type="performance",
            status=status,
            message="Performance check completed" if status == ValidationStatus.PASS else "Performance issues found",
            errors=errors,
            warnings=warnings,
        )
        
        self.results.append(result)
        return result
    
    def get_all_results(self) -> List[ValidationResult]:
        """Get all validation results"""
        return self.results
    
    def get_errors(self) -> List[BuildError]:
        """Get all collected errors"""
        return self.errors
    
    def clear_results(self):
        """Clear validation results"""
        self.results.clear()
        self.errors.clear()
    
    def run_all_validations(self) -> Dict[str, ValidationResult]:
        """Run all validations and return results"""
        return {
            "syntax": self.run_syntax_check(),
            "type": self.run_type_check(),
            "lint": self.run_lint(),
            "build": self.run_build(),
            "accessibility": self.run_accessibility_check(),
            "performance": self.run_performance_check(),
        }
