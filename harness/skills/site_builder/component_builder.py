"""
Component Builder - Component creation and reuse logic
"""
from typing import Dict, List, Optional, Any

from .models import ProjectSnapshot
from .file_manager import FileManager
from .code_generator import CodeGenerator


class ComponentBuilder:
    """Builds components following reuse priority rules"""
    
    def __init__(self, project_path: str, snapshot: Optional[ProjectSnapshot] = None):
        self.file_manager = FileManager(project_path)
        self.snapshot = snapshot
        self.code_generator = CodeGenerator()
        self.created_components: List[str] = []
        self.reused_components: List[str] = []
    
    def find_existing_component(self, name: str) -> Optional[str]:
        """Find an existing component by name"""
        if not self.snapshot or not self.snapshot.components:
            return None
        
        for comp in self.snapshot.components:
            if comp.get("name", "").lower() == name.lower():
                return comp.get("path")
        
        return None
    
    def should_reuse(self, name: str, existing_path: str, 
                    required_props: Optional[List[str]] = None) -> bool:
        """Determine if an existing component should be reused"""
        # Read the component file to analyze
        content = self.file_manager.read_file(existing_path)
        
        if not content:
            return False
        
        # Check if component has required props
        if required_props:
            for prop in required_props:
                if prop not in content:
                    return False
        
        # Component exists and is compatible - reuse it
        return True
    
    def adapt_component(self, name: str, existing_path: str,
                       adaptations: Dict[str, Any]) -> str:
        """Adapt an existing component to new requirements"""
        content = self.file_manager.read_file(existing_path)
        
        if not content:
            raise FileNotFoundError(f"Component not found: {existing_path}")
        
        modified_content = content
        
        # Apply adaptations (this is simplified - real implementation would use AST)
        if "styles" in adaptations:
            # Replace style classes
            pass
        
        if "props" in adaptations:
            # Add or modify props
            pass
        
        return modified_content
    
    def create_component(self, name: str, props: Optional[Dict[str, str]] = None,
                        content: Optional[str] = None,
                        styles: Optional[str] = None,
                        path: Optional[str] = None) -> str:
        """Create a new component"""
        # Default path
        if not path:
            path = f"src/components/{name}.tsx"
        
        # Generate component code
        component_code = self.code_generator.generate_component(
            name=name,
            props=props,
            content=content,
            styles=styles
        )
        
        # Create the component file
        self.file_manager.create_file(path, component_code, reason=f"Create component: {name}")
        
        # Create CSS module if styles provided
        if styles:
            css_path = path.replace('.tsx', '.module.css').replace('.jsx', '.module.css')
            css_code = self.code_generator.generate_css_module(name, styles)
            self.file_manager.create_file(css_path, css_code, reason=f"Create styles for: {name}")
        
        self.created_components.append(name)
        return path
    
    def build_component(self, component_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Build a component from a ComponentPlan"""
        name = component_plan.get("name", "UnknownComponent")
        props = component_plan.get("props", {})
        variants = component_plan.get("variants", [])
        states = component_plan.get("states", [])
        responsive_behavior = component_plan.get("responsive_behavior", {})
        accessibility = component_plan.get("accessibility", {})
        animation = component_plan.get("animation", {})
        source_resource = component_plan.get("source_resource")
        
        # Priority 1: Check for existing component to reuse
        existing_path = self.find_existing_component(name)
        
        if existing_path:
            # Priority 2: Try to adapt existing
            if self.should_reuse(name, existing_path, list(props.keys()) if props else None):
                self.reused_components.append(name)
                return {
                    "action": "reused",
                    "component_name": name,
                    "path": existing_path,
                }
            
            # Adapt the component
            try:
                adapted_content = self.adapt_component(name, existing_path, {
                    "props": props,
                    "styles": responsive_behavior,
                })
                
                # Save adapted version
                self.file_manager.modify_file(
                    existing_path,
                    self.file_manager.read_file(existing_path) or "",
                    adapted_content,
                    reason=f"Adapt component: {name}"
                )
                
                self.reused_components.append(name)
                return {
                    "action": "adapted",
                    "component_name": name,
                    "path": existing_path,
                }
            except Exception:
                pass  # Fall through to create new
        
        # Priority 5: Create custom component
        created_path = self.create_component(
            name=name,
            props=props,
            content=None,  # Will use default
            styles=None,
        )
        
        return {
            "action": "created",
            "component_name": name,
            "path": created_path,
        }
    
    def get_created_components(self) -> List[str]:
        """Get list of created component names"""
        return self.created_components
    
    def get_reused_components(self) -> List[str]:
        """Get list of reused component names"""
        return self.reused_components
    
    def get_all_changes(self):
        """Get all file changes made"""
        return self.file_manager.get_all_changes()
