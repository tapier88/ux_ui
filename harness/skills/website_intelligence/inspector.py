"""
Website Intelligence - Inspector for analyzing websites
"""
from typing import Dict, Any, Optional, List
import os

from .models import (
    WebsiteDesignProfile,
    TechnologyStack,
    VisualDesign,
    Typography,
    Layout,
    ComponentLibrary,
    AccessibilityInfo,
    PerformanceMetrics,
    AIQualityScore,
    DesignStyle,
    ColorPalette,
    ColorInfo
)


class WebsiteInspector:
    """Inspects websites and extracts design information"""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path
        self._cache: Dict[str, Any] = {}
    
    def inspect(self, url: Optional[str] = None) -> WebsiteDesignProfile:
        """
        Inspect a website and return a complete design profile.
        
        If project_path is set, inspects local files.
        If url is provided, attempts to fetch remote info.
        Returns UNKNOWN/EMPTY values when information is not available.
        """
        profile = WebsiteDesignProfile(
            project_name=self._extract_project_name(),
            url=url,
            technology_stack=self._inspect_technology(),
            visual_design=self._inspect_visual(),
            typography=self._inspect_typography(),
            layout=self._inspect_layout(),
            component_library=self._inspect_components(),
            accessibility=self._inspect_accessibility(),
            performance=self._inspect_performance(),
            ai_quality=self._inspect_ai_quality(),
            patterns=self._extract_patterns(),
            motion_effects=self._extract_motion_effects(),
            assets=self._extract_assets()
        )
        
        return profile
    
    def _extract_project_name(self) -> str:
        """Extract project name from path or return unknown"""
        if self.project_path and os.path.exists(self.project_path):
            return os.path.basename(self.project_path) or "unknown"
        return "unknown"
    
    def _inspect_technology(self) -> Optional[TechnologyStack]:
        """Inspect technology stack"""
        if not self.project_path:
            return None
        
        tech_stack = TechnologyStack()
        
        # Check for package.json
        package_json_path = os.path.join(self.project_path, "package.json")
        if os.path.exists(package_json_path):
            try:
                import json
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                    
                deps = package_data.get("dependencies", {})
                dev_deps = package_data.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}
                
                # Detect frontend frameworks
                if "react" in all_deps or "react-dom" in all_deps:
                    tech_stack.frontend_frameworks.append("React")
                if "vue" in all_deps:
                    tech_stack.frontend_frameworks.append("Vue")
                if "angular" in all_deps or "@angular/core" in all_deps:
                    tech_stack.frontend_frameworks.append("Angular")
                if "next" in all_deps:
                    tech_stack.frontend_frameworks.append("Next.js")
                if "nuxt" in all_deps:
                    tech_stack.frontend_frameworks.append("Nuxt")
                if "svelte" in all_deps:
                    tech_stack.frontend_frameworks.append("Svelte")
                
                # Detect CSS frameworks
                if "tailwindcss" in all_deps:
                    tech_stack.css_frameworks.append("Tailwind CSS")
                if "bootstrap" in all_deps:
                    tech_stack.css_frameworks.append("Bootstrap")
                if "@mui/material" in all_deps:
                    tech_stack.css_frameworks.append("Material-UI")
                if "@chakra-ui/react" in all_deps:
                    tech_stack.css_frameworks.append("Chakra UI")
                
                # Detect build tools
                if "webpack" in all_deps:
                    tech_stack.build_tools.append("Webpack")
                if "vite" in all_deps:
                    tech_stack.build_tools.append("Vite")
                if "esbuild" in all_deps:
                    tech_stack.build_tools.append("esbuild")
                if "rollup" in all_deps:
                    tech_stack.build_tools.append("Rollup")
                    
            except Exception:
                pass
        
        # Check for requirements.txt (Python backend)
        requirements_path = os.path.join(self.project_path, "requirements.txt")
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    for line in f:
                        line = line.strip().lower()
                        if "django" in line:
                            tech_stack.backend_technologies.append("Django")
                        elif "flask" in line:
                            tech_stack.backend_technologies.append("Flask")
                        elif "fastapi" in line:
                            tech_stack.backend_technologies.append("FastAPI")
            except Exception:
                pass
        
        # Check for common CMS indicators
        if os.path.exists(os.path.join(self.project_path, "wp-config.php")):
            tech_stack.cms = "WordPress"
        elif os.path.exists(os.path.join(self.project_path, "craftcms")):
            tech_stack.cms = "Craft CMS"
        
        # Return None if no technologies found
        if (not tech_stack.frontend_frameworks and 
            not tech_stack.backend_technologies and
            not tech_stack.css_frameworks and
            not tech_stack.build_tools and
            tech_stack.hosting_platform == "unknown" and
            tech_stack.cms is None and
            not tech_stack.analytics):
            return None
            
        return tech_stack
    
    def _inspect_visual(self) -> Optional[VisualDesign]:
        """Inspect visual design"""
        if not self.project_path:
            return None
        
        visual = VisualDesign()
        
        # Try to detect style from CSS files
        css_files = self._find_css_files()
        if css_files:
            styles_detected = set()
            for css_file in css_files[:5]:  # Check first 5 CSS files
                try:
                    with open(css_file, 'r') as f:
                        content = f.read().lower()
                        
                    if "border-radius" in content and content.count("border-radius") > 10:
                        styles_detected.add("modern")
                    if "box-shadow" in content:
                        styles_detected.add("modern")
                    if "gradient" in content or "linear-gradient" in content:
                        styles_detected.add("bold")
                    if "serif" in content:
                        styles_detected.add("classic")
                    if "minimal" in content or "simple" in content:
                        styles_detected.add("minimalist")
                except Exception:
                    pass
            
            if styles_detected:
                primary_style = list(styles_detected)[0]
                try:
                    visual.style = DesignStyle(primary_style)
                except ValueError:
                    visual.style = DesignStyle.UNKNOWN
        
        # Try to extract colors from CSS
        colors = self._extract_colors_from_css()
        if colors:
            visual.color_palette = ColorPalette(
                colors=colors,
                dominant_color=colors[0].hex if colors else None
            )
        
        # Return None if no visual info found
        if visual.style == DesignStyle.UNKNOWN and visual.color_palette is None:
            return None
            
        return visual
    
    def _inspect_typography(self) -> Optional[Typography]:
        """Inspect typography"""
        if not self.project_path:
            return None
        
        typography = Typography()
        
        css_files = self._find_css_files()
        fonts_found = set()
        
        for css_file in css_files[:5]:
            try:
                with open(css_file, 'r') as f:
                    content = f.read()
                    
                # Extract font-family declarations
                import re
                font_matches = re.findall(r'font-family:\s*([^;]+);', content, re.IGNORECASE)
                for match in font_matches:
                    fonts = [f.strip().strip('"').strip("'") for f in match.split(',')]
                    fonts_found.update(fonts)
                    
                # Extract font sizes
                size_matches = re.findall(r'font-size:\s*([^;]+);', content, re.IGNORECASE)
                if size_matches:
                    typography.font_sizes["body"] = size_matches[0].strip()
                    
            except Exception:
                pass
        
        if fonts_found:
            typography.font_families = list(fonts_found)[:10]  # Limit to 10 fonts
        
        if not typography.font_families and not typography.font_sizes:
            return None
            
        return typography
    
    def _inspect_layout(self) -> Optional[Layout]:
        """Inspect layout"""
        if not self.project_path:
            return None
        
        layout = Layout()
        
        css_files = self._find_css_files()
        
        for css_file in css_files[:5]:
            try:
                with open(css_file, 'r') as f:
                    content = f.read().lower()
                
                if "display: grid" in content or "display:grid" in content:
                    layout.grid_type = "grid"
                elif "display: flex" in content or "display:flex" in content:
                    layout.grid_type = "flex"
                elif "float:" in content:
                    layout.grid_type = "float"
                
                # Try to detect columns
                import re
                col_matches = re.findall(r'grid-template-columns:\s*([^;]+);', content)
                if col_matches:
                    cols = col_matches[0].strip()
                    layout.columns = cols.count(' ') + 1 if ' ' in cols else 1
                    
            except Exception:
                pass
        
        if layout.grid_type == "unknown" and layout.columns == 0:
            return None
            
        return layout
    
    def _inspect_components(self) -> Optional[ComponentLibrary]:
        """Inspect component library"""
        if not self.project_path:
            return None
        
        components = ComponentLibrary()
        
        # Look for component directories
        component_dirs = ["components", "src/components", "app/components", "ui"]
        
        for comp_dir in component_dirs:
            full_path = os.path.join(self.project_path, comp_dir)
            if os.path.exists(full_path):
                try:
                    for item in os.listdir(full_path):
                        if item.endswith(('.tsx', '.jsx', '.vue', '.svelte', '.py')):
                            comp_name = os.path.splitext(item)[0]
                            components.components.append(comp_name)
                except Exception:
                    pass
        
        components.component_count = len(components.components)
        
        if components.component_count == 0:
            return None
            
        return components
    
    def _inspect_accessibility(self) -> Optional[AccessibilityInfo]:
        """Inspect accessibility"""
        # Without actual HTML parsing, return basic info
        return AccessibilityInfo(
            wcag_level="unknown",
            compliance_score=0.0,
            issues=[],
            recommendations=["Run automated accessibility testing"]
        )
    
    def _inspect_performance(self) -> Optional[PerformanceMetrics]:
        """Inspect performance metrics"""
        # Without actual performance testing, return empty
        return PerformanceMetrics(
            load_time=0.0,
            lighthouse_score=0
        )
    
    def _inspect_ai_quality(self) -> Optional[AIQualityScore]:
        """Inspect AI quality score"""
        # Default AI quality assessment
        return AIQualityScore(
            overall_score=0.0,
            ai_confidence=0.0,
            notes=["Manual review required"]
        )
    
    def _extract_patterns(self) -> List[str]:
        """Extract design patterns"""
        patterns = []
        
        if not self.project_path:
            return patterns
        
        # Look for common pattern indicators
        css_files = self._find_css_files()
        
        for css_file in css_files[:3]:
            try:
                with open(css_file, 'r') as f:
                    content = f.read().lower()
                
                if "hero" in content:
                    patterns.append("hero-section")
                if "card" in content:
                    patterns.append("card-layout")
                if "modal" in content or "dialog" in content:
                    patterns.append("modal")
                if "accordion" in content:
                    patterns.append("accordion")
                if "carousel" in content or "slider" in content:
                    patterns.append("carousel")
                    
            except Exception:
                pass
        
        return list(set(patterns))
    
    def _extract_motion_effects(self) -> List[str]:
        """Extract motion effects"""
        effects = []
        
        if not self.project_path:
            return effects
        
        css_files = self._find_css_files()
        
        for css_file in css_files[:3]:
            try:
                with open(css_file, 'r') as f:
                    content = f.read().lower()
                
                if "@keyframes" in content:
                    effects.append("animations")
                if "transition:" in content or "transition:" in content:
                    effects.append("transitions")
                if "transform:" in content:
                    effects.append("transforms")
                    
            except Exception:
                pass
        
        return list(set(effects))
    
    def _extract_assets(self) -> Dict[str, Any]:
        """Extract asset information"""
        assets = {
            "images": [],
            "fonts": [],
            "videos": [],
            "icons": []
        }
        
        if not self.project_path:
            return assets
        
        # Look for asset directories
        asset_dirs = ["assets", "public", "static", "src/assets", "images", "img"]
        
        for asset_dir in asset_dirs:
            full_path = os.path.join(self.project_path, asset_dir)
            if os.path.exists(full_path):
                try:
                    for item in os.listdir(full_path):
                        if item.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                            assets["images"].append(item)
                        elif item.endswith(('.woff', '.woff2', '.ttf', '.eot')):
                            assets["fonts"].append(item)
                        elif item.endswith(('.mp4', '.webm', '.ogg')):
                            assets["videos"].append(item)
                        elif item.endswith(('.ico', '.svg')) and 'icon' in item.lower():
                            assets["icons"].append(item)
                except Exception:
                    pass
        
        return assets
    
    def _find_css_files(self) -> List[str]:
        """Find CSS files in the project"""
        css_files = []
        
        if not self.project_path:
            return css_files
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip node_modules, harness bookkeeping, and other large/
            # irrelevant directories. .harness/ specifically holds this
            # tool's own checkpoints - without excluding it, inspecting the
            # same project twice in a row (inspect -> build -> inspect
            # again) picks up files the harness itself wrote as if they
            # were part of the project, changing the detected profile
            # between runs on an otherwise-unchanged project.
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'dist', 'build', '.harness']]
            
            for file in files:
                if file.endswith('.css') or file.endswith('.scss') or file.endswith('.sass'):
                    css_files.append(os.path.join(root, file))
                    
                    if len(css_files) >= 10:  # Limit to 10 files
                        return css_files
        
        return css_files
    
    def _extract_colors_from_css(self) -> List[ColorInfo]:
        """Extract colors from CSS files"""
        colors = []
        
        css_files = self._find_css_files()
        
        for css_file in css_files[:3]:
            try:
                with open(css_file, 'r') as f:
                    content = f.read()
                
                import re
                
                # Find hex colors
                hex_matches = re.findall(r'#([0-9a-fA-F]{3,8})\b', content)
                for hex_val in hex_matches[:10]:  # Limit colors
                    if len(hex_val) == 3:
                        hex_val = ''.join([c*2 for c in hex_val])
                    elif len(hex_val) == 4:
                        hex_val = ''.join([c*2 for c in hex_val[:3]])
                    elif len(hex_val) == 8:
                        hex_val = hex_val[:6]
                    
                    colors.append(ColorInfo(hex=f"#{hex_val}"))
                    
            except Exception:
                pass
        
        return colors[:10]  # Return max 10 colors
