"""
Section Builder - Section implementation from SectionPlan
"""
from typing import Dict, List, Optional, Any

from .file_manager import FileManager
from .code_generator import CodeGenerator


class SectionBuilder:
    """Builds sections following SectionPlan specifications"""
    
    def __init__(self, project_path: str):
        self.file_manager = FileManager(project_path)
        self.code_generator = CodeGenerator()
        self.created_sections: List[str] = []
    
    def build_section(self, section_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Build a section from a SectionPlan"""
        section_id = section_plan.get("id", "section")
        layout = section_plan.get("layout", {})
        if isinstance(layout, str):
            # DesignExecutionPlanner emits a plain layout label (e.g.
            # "standard", "grid", "centered") rather than a structured
            # object — normalize here so a string label is a valid
            # SectionPlan just like a full {"type": ..., ...} dict.
            layout = {"type": layout}
        content = section_plan.get("content", {})
        components = section_plan.get("components", [])
        components = [
            comp if isinstance(comp, dict) else {"name": self._to_component_name(comp)}
            for comp in components
        ]
        assets = section_plan.get("assets", [])
        background = section_plan.get("background", {})
        typography = section_plan.get("typography", {})
        motion = section_plan.get("motion", {})
        if isinstance(motion, list):
            # DesignExecutionPlanner emits motion as a plain list of
            # effect names (e.g. ["fade-in", "slide-up"]) rather than a
            # structured {"enabled": bool, ...} object.
            motion = {"enabled": bool(motion), "effects": motion}
        responsive_behavior = section_plan.get("responsive_behavior", {})
        
        # Generate section component
        section_name = section_plan.get("name", f"Section{section_id.title().replace('-', '')}")
        # Section names from DesignExecutionPlanner can contain spaces
        # (e.g. "Trust Indicators") — not valid as a bare .tsx filename
        # or JS component identifier on every platform/bundler. Reuse
        # the same slug->PascalCase normalization applied to components.
        section_name = self._to_component_name(section_name)
        
        # Create section code based on layout type
        layout_type = layout.get("type", "container")
        section_code = self._generate_section_code(
            name=section_name,
            layout_type=layout_type,
            layout=layout,
            content=content,
            components=components,
            background=background,
            typography=typography,
            motion=motion,
            responsive=responsive_behavior,
        )
        
        # Determine path based on framework
        section_path = f"src/components/sections/{section_name}.tsx"
        
        # Create the section file
        self.file_manager.create_file(
            section_path, 
            section_code, 
            reason=f"Create section: {section_name}"
        )
        
        self.created_sections.append(section_name)
        
        return {
            "action": "created",
            "section_name": section_name,
            "path": section_path,
            "layout_type": layout_type,
        }
    
    def _generate_section_code(self, name: str, layout_type: str,
                              layout: Dict[str, Any], content: Dict[str, Any],
                              components: List[Dict[str, Any]],
                              background: Dict[str, Any],
                              typography: Dict[str, Any],
                              motion: Dict[str, Any],
                              responsive: Dict[str, Any]) -> str:
        """Generate section component code"""
        
        # Build classes based on layout type
        classes = self._build_layout_classes(layout_type, layout)
        
        # Add background classes
        if background:
            bg_color = background.get("color", "")
            if bg_color:
                classes.append(bg_color)
        
        # Build motion props if motion is specified
        motion_props = ""
        if motion and motion.get("enabled", False):
            motion_props = self._build_motion_props(motion)
        
        # Build responsive classes
        responsive_classes = self._build_responsive_classes(responsive)
        all_classes = classes + responsive_classes
        
        # Generate content
        content_html = self._generate_content_html(content)
        
        # Generate component imports
        component_imports = self._generate_component_imports(components)
        
        # Motion import if needed
        motion_import = ""
        if motion and motion.get("enabled", False):
            motion_import = "import { motion } from 'framer-motion';\n"
        
        return f"""{motion_import}{component_imports}import React from 'react';

interface {name}Props {{
  className?: string;
}}

export const {name}: React.FC<{name}Props> = ({{ className }}) => {{
  return (
    <section className="{name.lower()} {' '.join(all_classes)} ${{className || ''}}">
      {self._generate_section_inner(content_html, components, motion_props)}
    </section>
  );
}};

export default {name};
"""
    
    def _build_layout_classes(self, layout_type: str, layout: Dict[str, Any]) -> List[str]:
        """Build Tailwind classes based on layout type"""
        classes = []
        
        if layout_type == "grid":
            cols = layout.get("columns", 12)
            gap = layout.get("gap", "gap-8")
            classes.extend(["grid", f"grid-cols-{min(cols, 12)}", gap])
        elif layout_type == "flex":
            direction = layout.get("direction", "row")
            justify = layout.get("justify", "center")
            align = layout.get("align", "center")
            classes.extend([
                "flex",
                f"flex-{direction}",
                f"justify-{justify}",
                f"items-{align}",
            ])
        elif layout_type == "container":
            max_width = layout.get("maxWidth", "7xl")
            classes.extend(["container", f"mx-auto", f"max-w-{max_width}", "px-4"])
        elif layout_type == "full-bleed":
            classes.extend(["w-full"])
        elif layout_type == "asymmetric":
            # Asymmetric layouts use custom grid/flex configurations
            classes.extend(["grid", "grid-cols-1", "md:grid-cols-3", "gap-8"])
        elif layout_type == "bento":
            classes.extend(["grid", "grid-cols-1", "md:grid-cols-2", "lg:grid-cols-4", "gap-4"])
        else:
            classes.extend(["container", "mx-auto", "px-4"])
        
        return classes
    
    def _build_motion_props(self, motion: Dict[str, Any]) -> str:
        """Build motion animation props"""
        initial = motion.get("initial", {})
        animate = motion.get("animate", {})
        transition = motion.get("transition", {})
        
        props = []
        
        if initial:
            initial_str = ", ".join([f"{k}: {repr(v)}" for k, v in initial.items()])
            props.append(f'initial={{ {{ {initial_str} }} }}')
        
        if animate:
            animate_str = ", ".join([f"{k}: {repr(v)}" for k, v in animate.items()])
            props.append(f'animate={{ {{ {animate_str} }} }}')
        
        if transition:
            transition_str = ", ".join([f"{k}: {repr(v)}" for k, v in transition.items()])
            props.append(f'transition={{ {{ {transition_str} }} }}')
        
        return " ".join(props)
    
    def _build_responsive_classes(self, responsive: Dict[str, Any]) -> List[str]:
        """Build responsive behavior classes"""
        classes = []

        # DesignExecutionPlanner emits each breakpoint as a plain string
        # shorthand (e.g. {"mobile": "stack"}) rather than a structured
        # {"stack": True, "hidden": False, ...} object — normalize each
        # breakpoint the same way regardless of which shorthand form it
        # arrives in, instead of assuming a dict everywhere.
        def _as_dict(value: Any) -> Dict[str, Any]:
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                # A bare string names the one behavior it requests
                # (e.g. "stack", "hidden") — treat it as that flag.
                return {value: True}
            return {}

        # Mobile
        mobile = _as_dict(responsive.get("mobile", {}))
        if mobile.get("hidden", False):
            classes.append("hidden")
        if mobile.get("stack", False):
            classes.extend(["flex", "flex-col"])
        
        # Tablet
        tablet = _as_dict(responsive.get("tablet", {}))
        if tablet.get("cols"):
            classes.append(f"md:grid-cols-{tablet['cols']}")
        
        # Desktop
        desktop = _as_dict(responsive.get("desktop", {}))
        if desktop.get("cols"):
            classes.append(f"lg:grid-cols-{desktop['cols']}")
        
        return classes
    
    def _generate_content_html(self, content: Dict[str, Any]) -> str:
        """Generate content HTML/JSX"""
        elements = []
        
        if "title" in content:
            title = content["title"]
            elements.append(f"<h2>{title}</h2>")
        
        if "subtitle" in content:
            subtitle = content["subtitle"]
            elements.append(f"<p className=\"text-lg text-gray-600\">{subtitle}</p>")
        
        if "body" in content:
            body = content["body"]
            elements.append(f"<div className=\"prose\">{body}</div>")
        
        if "cta" in content:
            cta = content["cta"]
            elements.append(f'<button className="btn-primary">{cta.get("text", "Click")}</button>')
        
        return "\n      ".join(elements) if elements else "{/* Content goes here */}"
    
    def _generate_section_inner(self, content_html: str, 
                               components: List[Dict[str, Any]],
                               motion_props: str) -> str:
        """Generate section inner content"""
        wrapper_open = "<div"
        if motion_props:
            wrapper_open = "<motion.div"
            wrapper_open += f" {motion_props}"
        wrapper_open += ' className="inner">'
        
        wrapper_close = "</motion.div>" if motion_props else "</div>"
        
        component_usage = ""
        for comp in components:
            comp_name = comp.get("name", "Component")
            component_usage += f"\n      <{comp_name} />"
        
        return f"{wrapper_open}\n      {content_html}{component_usage}\n      {wrapper_close}"
    
    def _generate_component_imports(self, components: List[Dict[str, Any]]) -> str:
        """Generate component import statements"""
        imports = []
        
        for comp in components:
            name = comp.get("name", "")
            if name:
                imports.append(f"import {{ {name} }} from '@/components/{name}';")
        
        return "\n".join(imports) + "\n" if imports else ""
    
    def get_created_sections(self) -> List[str]:
        """Get list of created section names"""
        return self.created_sections

    @staticmethod
    def _to_component_name(raw: str) -> str:
        """Turn a plain component-name string like 'cta-button' or
        'hero-image' into a PascalCase component name ('CtaButton',
        'HeroImage') — DesignExecutionPlanner emits component slugs as
        plain strings, not {"name": ...} objects."""
        parts = str(raw).replace("_", "-").replace(" ", "-").split("-")
        return "".join(p.capitalize() for p in parts if p) or "Component"
