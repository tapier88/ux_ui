"""
Project Inspector - Analyzes existing projects to understand structure and architecture
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from .models import (
    ProjectSnapshot,
    Framework,
    PackageManager,
    BuildTool,
)


class ProjectInspector:
    """Inspects project structure and detects framework, dependencies, architecture"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.snapshot: Optional[ProjectSnapshot] = None
    
    def inspect(self) -> ProjectSnapshot:
        """Perform full project inspection"""
        snapshot = ProjectSnapshot(root_path=str(self.project_path))
        
        # Detect package manager and dependencies
        self._inspect_package_json(snapshot)
        
        # Detect framework
        self._detect_framework(snapshot)
        
        # Detect build tool
        self._detect_build_tool(snapshot)
        
        # Inspect project structure
        self._inspect_structure(snapshot)
        
        # Inspect routes
        self._inspect_routes(snapshot)
        
        # Inspect components
        self._inspect_components(snapshot)
        
        # Inspect styles
        self._inspect_styles(snapshot)
        
        # Inspect assets
        self._inspect_assets(snapshot)
        
        # Detect design system
        self._detect_design_system(snapshot)
        
        # Detect architecture
        self._detect_architecture(snapshot)
        
        self.snapshot = snapshot
        return snapshot
    
    def _inspect_package_json(self, snapshot: ProjectSnapshot):
        """Inspect package.json for dependencies and scripts"""
        package_json_path = self.project_path / "package.json"
        
        if not package_json_path.exists():
            snapshot.package_manager = PackageManager.NONE
            return
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Detect package manager from lock file
            if (self.project_path / "package-lock.json").exists():
                snapshot.package_manager = PackageManager.NPM
            elif (self.project_path / "pnpm-lock.yaml").exists():
                snapshot.package_manager = PackageManager.PNPM
            elif (self.project_path / "yarn.lock").exists():
                snapshot.package_manager = PackageManager.YARN
            elif (self.project_path / "bun.lockb").exists():
                snapshot.package_manager = PackageManager.BUN
            
            # Get dependencies
            snapshot.dependencies = package_data.get("dependencies", {})
            snapshot.dev_dependencies = package_data.get("devDependencies", {})
            
            # Get scripts
            snapshot.scripts = package_data.get("scripts", {})
            
            # Detect language
            ts_config = self.project_path / "tsconfig.json"
            if ts_config.exists():
                snapshot.language = "typescript"
            else:
                snapshot.language = "javascript"
                
        except (json.JSONDecodeError, IOError):
            pass
    
    def _detect_framework(self, snapshot: ProjectSnapshot):
        """Detect the framework used in the project"""
        all_deps = {**snapshot.dependencies, **snapshot.dev_dependencies}
        
        # Check for Next.js
        if "next" in all_deps:
            snapshot.framework = Framework.NEXT_JS
            return
        
        # Check for React + Vite
        if "vite" in all_deps and "react" in all_deps:
            snapshot.framework = Framework.VITE
            return
        
        # Check for React only (CRA or custom)
        if "react" in all_deps:
            if "@vitejs/plugin-react" in all_deps:
                snapshot.framework = Framework.VITE
            elif "react-scripts" in all_deps:
                snapshot.framework = Framework.CRA
            else:
                snapshot.framework = Framework.REACT
            return
        
        # Check for Vue
        if "vue" in all_deps:
            if "vite" in all_deps:
                snapshot.framework = Framework.VITE
            snapshot.framework = Framework.VUE
            return
        
        # Check for Astro
        if "astro" in all_deps:
            snapshot.framework = Framework.ASTRO
            return
        
        # Check for HTML/CSS/JS (no framework)
        src_dir = self.project_path / "src"
        app_dir = self.project_path / "app"
        
        if not src_dir.exists() and not app_dir.exists():
            # Check for index.html at root
            if (self.project_path / "index.html").exists():
                snapshot.framework = Framework.HTML_CSS_JS
                return
        
        snapshot.framework = Framework.UNKNOWN
    
    def _detect_build_tool(self, snapshot: ProjectSnapshot):
        """Detect the build tool used"""
        all_deps = {**snapshot.dependencies, **snapshot.dev_dependencies}
        
        if "next" in all_deps:
            snapshot.build_tool = BuildTool.NEXT_BUILD
        elif "vite" in all_deps:
            snapshot.build_tool = BuildTool.VITE_BUILD
        elif "webpack" in all_deps:
            snapshot.build_tool = BuildTool.WEBPACK
        elif "astro" in all_deps:
            snapshot.build_tool = BuildTool.ASTRO_BUILD
        elif "react-scripts" in all_deps:
            snapshot.build_tool = BuildTool.CRA
        else:
            snapshot.build_tool = BuildTool.NONE
    
    def _inspect_structure(self, snapshot: ProjectSnapshot):
        """Inspect project directory structure"""
        # Find entry points
        entry_points = []
        
        for name in ["index.html", "main.tsx", "main.ts", "index.tsx", "index.ts", 
                     "main.jsx", "index.jsx", "app.tsx", "app.ts"]:
            path = self.project_path / "src" / name
            if path.exists():
                entry_points.append(str(path.relative_to(self.project_path)))
            
            path = self.project_path / name
            if path.exists():
                entry_points.append(str(path.relative_to(self.project_path)))
        
        snapshot.entry_points = entry_points
    
    def _inspect_routes(self, snapshot: ProjectSnapshot):
        """Inspect routes in the project"""
        routes = []
        
        # Next.js app router
        app_dir = self.project_path / "app"
        if app_dir.exists():
            for path in app_dir.rglob("page.*"):
                route = str(path.relative_to(app_dir).parent)
                if route == ".":
                    route = "/"
                routes.append(route)
        
        # Next.js pages router or React Router
        pages_dir = self.project_path / "pages"
        if pages_dir.exists():
            for path in pages_dir.rglob("*.*"):
                if path.is_file() and path.stem != "_app" and path.stem != "_document":
                    route = str(path.relative_to(pages_dir))
                    route = route.rsplit(".", 1)[0]  # Remove extension
                    if route == "index":
                        route = "/"
                    routes.append("/" + route.lstrip("/"))
        
        snapshot.routes = routes[:20]  # Limit to 20 routes
    
    def _inspect_components(self, snapshot: ProjectSnapshot):
        """Inspect components in the project"""
        components = []
        
        # Common component directories
        component_dirs = [
            self.project_path / "components",
            self.project_path / "src" / "components",
            self.project_path / "src" / "ui",
            self.project_path / "ui",
        ]
        
        for comp_dir in component_dirs:
            if comp_dir.exists():
                for path in comp_dir.rglob("*.tsx"):
                    rel_path = str(path.relative_to(self.project_path))
                    components.append({
                        "name": path.stem,
                        "path": rel_path,
                        "type": "tsx"
                    })
                for path in comp_dir.rglob("*.jsx"):
                    rel_path = str(path.relative_to(self.project_path))
                    components.append({
                        "name": path.stem,
                        "path": rel_path,
                        "type": "jsx"
                    })
                for path in comp_dir.rglob("*.vue"):
                    rel_path = str(path.relative_to(self.project_path))
                    components.append({
                        "name": path.stem,
                        "path": rel_path,
                        "type": "vue"
                    })
        
        snapshot.components = components[:50]  # Limit to 50 components
    
    def _inspect_styles(self, snapshot: ProjectSnapshot):
        """Inspect style files in the project"""
        styles = []
        
        style_dirs = [
            self.project_path / "styles",
            self.project_path / "src" / "styles",
            self.project_path / "css",
            self.project_path / "src" / "css",
            self.project_path / "app" / "styles",
        ]
        
        for style_dir in style_dirs:
            if style_dir.exists():
                for path in style_dir.rglob("*"):
                    if path.is_file() and path.suffix in [".css", ".scss", ".sass", ".less", ".styl"]:
                        styles.append(str(path.relative_to(self.project_path)))
        
        # Also check for global style files
        for name in ["globals.css", "global.css", "index.css", "styles.css"]:
            path = self.project_path / "src" / name
            if path.exists():
                styles.append(str(path.relative_to(self.project_path)))
        
        snapshot.styles = styles[:30]  # Limit to 30 style files
    
    def _inspect_assets(self, snapshot: ProjectSnapshot):
        """Inspect asset files in the project"""
        assets = []
        
        asset_dirs = [
            self.project_path / "public",
            self.project_path / "assets",
            self.project_path / "src" / "assets",
            self.project_path / "static",
        ]
        
        for asset_dir in asset_dirs:
            if asset_dir.exists():
                for path in asset_dir.rglob("*"):
                    if path.is_file() and path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".mp4", ".webm"]:
                        assets.append(str(path.relative_to(self.project_path)))
        
        snapshot.assets = assets[:50]  # Limit to 50 assets
    
    def _detect_design_system(self, snapshot: ProjectSnapshot):
        """Detect existing design system configuration"""
        design_system = {}
        
        # Check for Tailwind config
        tailwind_configs = ["tailwind.config.js", "tailwind.config.ts", "tailwind.config.cjs"]
        for config in tailwind_configs:
            path = self.project_path / config
            if path.exists():
                design_system["tailwind"] = True
                design_system["tailwind_config"] = config
                break
        
        # Check for theme files
        theme_files = ["theme.js", "theme.ts", "tokens.js", "tokens.ts"]
        for tf in theme_files:
            path = self.project_path / "src" / tf
            if path.exists():
                design_system["custom_theme"] = tf
                break
        
        # Check for CSS variables
        globals_css = self.project_path / "src" / "globals.css"
        if globals_css.exists():
            try:
                with open(globals_css, 'r') as f:
                    content = f.read()
                    if ":root" in content or "--" in content:
                        design_system["css_variables"] = True
            except IOError:
                pass
        
        snapshot.existing_design_system = design_system if design_system else None
    
    def _detect_architecture(self, snapshot: ProjectSnapshot):
        """Detect project architecture patterns"""
        architecture = {}
        
        # Check for common patterns
        src_dir = self.project_path / "src"
        
        if src_dir.exists():
            # Feature-based architecture
            features_dir = src_dir / "features"
            if features_dir.exists():
                architecture["pattern"] = "feature-based"
            
            # Domain-driven architecture
            domains_dir = src_dir / "domains"
            if domains_dir.exists():
                architecture["pattern"] = "domain-driven"
            
            # Layered architecture
            layers = ["controllers", "services", "repositories", "models"]
            found_layers = []
            for layer in layers:
                if (src_dir / layer).exists():
                    found_layers.append(layer)
            if found_layers:
                architecture["layers"] = found_layers
            
            # Check for atomic design
            atoms_dir = src_dir / "atoms"
            molecules_dir = src_dir / "molecules"
            if atoms_dir.exists() or molecules_dir.exists():
                architecture["pattern"] = "atomic-design"
        
        # Check for state management
        all_deps = {**snapshot.dependencies, **snapshot.dev_dependencies}
        if "redux" in all_deps or "@reduxjs/toolkit" in all_deps:
            architecture["state_management"] = "redux"
        elif "zustand" in all_deps:
            architecture["state_management"] = "zustand"
        elif "jotai" in all_deps:
            architecture["state_management"] = "jotai"
        elif "recoil" in all_deps:
            architecture["state_management"] = "recoil"
        
        snapshot.existing_architecture = architecture if architecture else None


def inspect_project(project_path: str) -> ProjectSnapshot:
    """Convenience function to inspect a project"""
    inspector = ProjectInspector(project_path)
    return inspector.inspect()
