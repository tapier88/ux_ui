"""
Dependency Manager - Dependency detection and installation
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import PackageManager


class DependencyManager:
    """Manages project dependencies with careful verification"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.dependencies_added: List[str] = []
        self.dependencies_removed: List[str] = []
        self.package_manager: Optional[PackageManager] = None
    
    def detect_package_manager(self) -> PackageManager:
        """Detect the package manager used in the project"""
        if (self.project_path / "package-lock.json").exists():
            self.package_manager = PackageManager.NPM
        elif (self.project_path / "pnpm-lock.yaml").exists():
            self.package_manager = PackageManager.PNPM
        elif (self.project_path / "yarn.lock").exists():
            self.package_manager = PackageManager.YARN
        elif (self.project_path / "bun.lockb").exists():
            self.package_manager = PackageManager.BUN
        elif (self.project_path / "package.json").exists():
            # Default to npm if no lock file
            self.package_manager = PackageManager.NPM
        else:
            self.package_manager = PackageManager.NONE
        
        return self.package_manager
    
    def get_install_command(self) -> str:
        """Get the install command for the detected package manager"""
        pm = self.detect_package_manager()
        
        commands = {
            PackageManager.NPM: "npm install",
            PackageManager.PNPM: "pnpm install",
            PackageManager.YARN: "yarn add",
            PackageManager.BUN: "bun add",
            PackageManager.NONE: "",
        }
        
        return commands.get(pm, "")
    
    def get_dev_install_command(self) -> str:
        """Get the dev dependency install command"""
        pm = self.detect_package_manager()
        
        commands = {
            PackageManager.NPM: "npm install --save-dev",
            PackageManager.PNPM: "pnpm install --save-dev",
            PackageManager.YARN: "yarn add --dev",
            PackageManager.BUN: "bun add --dev",
            PackageManager.NONE: "",
        }
        
        return commands.get(pm, "")
    
    def check_dependency_exists(self, package_name: str) -> bool:
        """Check if a dependency already exists in the project"""
        package_json_path = self.project_path / "package.json"
        
        if not package_json_path.exists():
            return False
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            
            return package_name in deps or package_name in dev_deps
        except (json.JSONDecodeError, IOError):
            return False
    
    def should_install(self, package_name: str, 
                      design_build_plan: Optional[Dict[str, Any]] = None) -> tuple[bool, str]:
        """Determine if a dependency should be installed"""
        # Check 1: Does it already exist?
        if self.check_dependency_exists(package_name):
            return False, "Already exists"
        
        # Check 2: Is it in DesignBuildPlan?
        if design_build_plan:
            plan_deps = design_build_plan.get("dependencies", [])
            required_deps = design_build_plan.get("required_dependencies", [])
            
            if package_name not in plan_deps and package_name not in required_deps:
                return False, "Not in DesignBuildPlan"
        
        # Check 3: Is there an alternative without dependency?
        # This would require a knowledge base of alternatives
        alternatives = {
            "framer-motion": ["CSS animations", "GSAP"],
            "gsap": ["CSS animations", "framer-motion"],
            "lodash": ["Native JS methods"],
        }
        
        if package_name in alternatives:
            # Log warning but allow installation
            pass
        
        return True, "Approved for installation"
    
    def install_dependency(self, package_name: str, version: Optional[str] = None,
                          is_dev: bool = False, reason: str = "") -> bool:
        """Install a dependency"""
        should_install_result, message = self.should_install(package_name)
        
        if not should_install_result:
            return False
        
        # Get install command
        if is_dev:
            cmd = self.get_dev_install_command()
        else:
            cmd = self.get_install_command()
        
        if not cmd:
            return False
        
        # Build full command
        package_spec = package_name
        if version:
            package_spec = f"{package_name}@{version}"
        
        full_cmd = f"{cmd} {package_spec}"
        
        try:
            # Execute installation
            result = subprocess.run(
                full_cmd.split(),
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.dependencies_added.append(package_spec)
                return True
            else:
                return False
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def install_dependencies(self, dependencies: List[Dict[str, Any]],
                            design_build_plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Install multiple dependencies from a list"""
        results = {
            "installed": [],
            "skipped": [],
            "failed": [],
        }
        
        for dep in dependencies:
            package_name = dep.get("name", "")
            version = dep.get("version")
            is_dev = dep.get("dev", False)
            reason = dep.get("reason", "")
            
            should_install_result, message = self.should_install(
                package_name, 
                design_build_plan
            )
            
            if not should_install_result:
                results["skipped"].append({
                    "package": package_name,
                    "reason": message,
                })
                continue
            
            success = self.install_dependency(
                package_name, 
                version, 
                is_dev,
                reason
            )
            
            if success:
                results["installed"].append({
                    "package": package_name,
                    "version": version,
                    "dev": is_dev,
                })
            else:
                results["failed"].append({
                    "package": package_name,
                    "reason": "Installation failed",
                })
        
        return results
    
    def remove_dependency(self, package_name: str) -> bool:
        """Remove a dependency"""
        pm = self.detect_package_manager()
        
        commands = {
            PackageManager.NPM: f"npm uninstall {package_name}",
            PackageManager.PNPM: f"pnpm uninstall {package_name}",
            PackageManager.YARN: f"yarn remove {package_name}",
            PackageManager.BUN: f"bun remove {package_name}",
            PackageManager.NONE: "",
        }
        
        cmd = commands.get(pm, "")
        if not cmd:
            return False
        
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.dependencies_removed.append(package_name)
                return True
            return False
        except Exception:
            return False
    
    def get_current_dependencies(self) -> Dict[str, str]:
        """Get current dependencies from package.json"""
        package_json_path = self.project_path / "package.json"
        
        if not package_json_path.exists():
            return {}
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            return {
                **package_data.get("dependencies", {}),
                **package_data.get("devDependencies", {}),
            }
        except (json.JSONDecodeError, IOError):
            return {}
    
    def get_dependencies_added(self) -> List[str]:
        """Get list of added dependencies"""
        return self.dependencies_added
    
    def get_dependencies_removed(self) -> List[str]:
        """Get list of removed dependencies"""
        return self.dependencies_removed
    
    def validate_bundle_impact(self, package_name: str) -> Dict[str, Any]:
        """Validate the bundle impact of a dependency (abstraction)"""
        # This is an abstraction - real implementation would:
        # 1. Analyze bundle size contribution
        # 2. Check tree-shaking support
        # 3. Evaluate code-splitting potential
        
        # Known bundle sizes (approximate in KB)
        known_sizes = {
            "framer-motion": {"size": 35, "gzipped": 12},
            "gsap": {"size": 45, "gzipped": 15},
            "three": {"size": 600, "gzipped": 180},
            "lodash": {"size": 70, "gzipped": 25},
            "react": {"size": 40, "gzipped": 13},
            "react-dom": {"size": 120, "gzipped": 40},
        }
        
        return known_sizes.get(package_name, {
            "size": "unknown",
            "gzipped": "unknown",
            "note": "Bundle size unknown - analyze with bundle analyzer",
        })
