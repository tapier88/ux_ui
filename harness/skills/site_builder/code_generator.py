"""
Code Generator - Generates code for components, sections, and utilities
"""
from typing import Dict, List, Optional, Any


class CodeGenerator:
    """Generates code snippets and files"""
    
    def __init__(self, framework: str = "react", language: str = "typescript"):
        self.framework = framework
        self.language = language
    
    def generate_component(self, name: str, props: Optional[Dict[str, str]] = None,
                          content: Optional[str] = None, 
                          styles: Optional[str] = None) -> str:
        """Generate a React/TypeScript component"""
        if self.language == "typescript":
            return self._generate_tsx_component(name, props, content, styles)
        else:
            return self._generate_jsx_component(name, props, content, styles)
    
    def _generate_tsx_component(self, name: str, props: Optional[Dict[str, str]] = None,
                               content: Optional[str] = None,
                               styles: Optional[str] = None) -> str:
        """Generate TypeScript JSX component"""
        props_type = ""
        props_interface = ""
        
        if props:
            interface_name = f"{name}Props"
            props_interface = f"interface {interface_name} {{\n"
            for prop_name, prop_type in props.items():
                props_interface += f"  {prop_name}: {prop_type};\n"
            props_interface += "}\n\n"
            props_type = f": {interface_name}"
        
        content_str = content or f"return <div className=\"{name.lower()}\">{name} Component</div>;"
        
        styles_import = ""
        if styles:
            styles_import = f"import './{name}.module.css';\n\n"
        
        return f"""{styles_import}import React from 'react';

{props_interface}export const {name}: React.FC<{props_type}> = (props) => {{
  {content_str}
}};

export default {name};
"""
    
    def _generate_jsx_component(self, name: str, props: Optional[Dict[str, str]] = None,
                               content: Optional[str] = None,
                               styles: Optional[str] = None) -> str:
        """Generate JavaScript JSX component"""
        props_destructure = ""
        
        if props:
            props_destructure = " = " + ", ".join([f"{k}" for k in props.keys()])
        
        content_str = content or f"return <div className=\"{name.lower()}\">{name} Component</div>;"
        
        return f"""import React from 'react';

export const {name} = (props{props_destructure}) => {{
  {content_str}
}};

export default {name};
"""
    
    def generate_css_module(self, name: str, styles: Optional[str] = None) -> str:
        """Generate CSS module file"""
        default_styles = f""".{name.lower()} {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}}
"""
        return styles or default_styles
    
    def generate_tailwind_classes(self, classes: List[str]) -> str:
        """Generate Tailwind class string"""
        return " ".join(classes)
    
    def generate_css_variables(self, tokens: Dict[str, Any]) -> str:
        """Generate CSS custom properties (variables) from a (possibly
        deeply nested) design tokens dict, e.g. {"colors": {"primary":
        "#000"}, "typography": {"h1": {"size": "3rem"}}} becomes
        --colors-primary: #000; --typography-h1-size: 3rem; etc.

        Previously this assumed a flat Dict[str, str] and simply
        interpolated whatever value it got directly into the CSS value
        position — when handed the real (nested) design_tokens dict
        produced by DesignExecutionPlanner, that meant writing Python's
        dict repr as a CSS value (invalid CSS). Recursing here fixes it
        at the point of generation rather than requiring every caller to
        pre-flatten its tokens.
        """
        flat_vars = self._flatten_tokens(tokens)
        css = ":root {\n"
        for name, value in flat_vars.items():
            css += f"  --{name}: {value};\n"
        css += "}\n"
        return css

    @classmethod
    def _flatten_tokens(cls, tokens: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
        """Recursively flatten a nested token dict into
        {css-custom-property-name: css-value} pairs."""
        flat: Dict[str, str] = {}
        for key, value in tokens.items():
            css_key = f"{prefix}-{key}" if prefix else str(key)
            if isinstance(value, dict):
                flat.update(cls._flatten_tokens(value, prefix=css_key))
            elif isinstance(value, (list, tuple)):
                flat[css_key] = ", ".join(str(v) for v in value)
            else:
                flat[css_key] = str(value)
        return flat
    
    def generate_tailwind_config(self, config: Dict[str, Any]) -> str:
        """Generate Tailwind configuration"""
        theme = config.get("theme", {})
        extend = theme.get("extend", {})
        
        tailwind_config = "/** @type {import('tailwindcss').Config} */\n"
        tailwind_config += "module.exports = {\n"
        tailwind_config += "  content: [\n"
        tailwind_config += '    "./src/**/*.{js,ts,jsx,tsx}",\n'
        tailwind_config += "  ],\n"
        tailwind_config += "  theme: {\n"
        tailwind_config += "    extend: {\n"
        
        if extend:
            for key, value in extend.items():
                if isinstance(value, dict):
                    tailwind_config += f"      {key}: {{\n"
                    for k, v in value.items():
                        tailwind_config += f"        '{k}': '{v}',\n"
                    tailwind_config += "      },\n"
                else:
                    tailwind_config += f"      {key}: {value},\n"
        
        tailwind_config += "    },\n"
        tailwind_config += "  },\n"
        tailwind_config += "  plugins: [],\n"
        tailwind_config += "}\n"
        
        return tailwind_config
    
    def generate_page(self, name: str, imports: Optional[List[str]] = None,
                     components: Optional[List[str]] = None,
                     content: Optional[str] = None) -> str:
        """Generate a page component"""
        imports_str = ""
        
        if imports:
            for imp in imports:
                imports_str += f"import {imp};\n"
        
        components_str = ""
        if components:
            for comp in components:
                components_str += f"import {comp} from '@/components/{comp}';\n"
        
        content_str = content or f"""  return (
    <main className="page-{name.lower()}">
      <h1>{name} Page</h1>
    </main>
  );"""
        
        return f"""{imports_str}{components_str}
export default function {name}Page() {{
{content_str}
}}
"""
    
    def generate_layout(self, name: str, children: str = "{children}") -> str:
        """Generate a layout component"""
        return f"""import React from 'react';

export default function {name}Layout({{ children }}) {{
  return (
    <div className="layout-{name.lower()}">
      {children}
    </div>
  );
}}
"""
    
    def generate_hook(self, name: str, content: str) -> str:
        """Generate a custom React hook"""
        if not name.startswith("use"):
            name = f"use{name}"
        
        return f"""import {{ useState, useEffect }} from 'react';

export function {name}() {{
{content}
}}
"""
    
    def generate_utility_function(self, name: str, params: str, return_type: str,
                                  body: str) -> str:
        """Generate a utility function"""
        if self.language == "typescript":
            return f"""export function {name}({params}): {return_type} {{
{body}
}}
"""
        else:
            return f"""export function {name}({params}) {{
{body}
}}
"""
    
    def generate_import_statement(self, module: str, 
                                 named_imports: Optional[List[str]] = None,
                                 default_import: Optional[str] = None,
                                 type_import: bool = False) -> str:
        """Generate an import statement"""
        if type_import and self.language == "typescript":
            if named_imports:
                return f"import type {{ {', '.join(named_imports)} }} from '{module}';"
            return f"import type {default_import} from '{module}';"
        
        parts = []
        
        if default_import:
            parts.append(default_import)
        
        if named_imports:
            parts.append(f"{{ {', '.join(named_imports)} }}")
        
        if parts:
            return f"import {' '.join(parts)} from '{module}';"
        
        return f"import '{module}';"
    
    def generate_export_statement(self, name: str, is_default: bool = True) -> str:
        """Generate an export statement"""
        if is_default:
            return f"export default {name};"
        return f"export {{ {name} }};"
    
    def generate_react_component_with_motion(self, name: str, 
                                            animations: Optional[Dict[str, Any]] = None) -> str:
        """Generate a React component with Motion animation"""
        motion_import = "import { motion } from 'framer-motion';\n\n"
        
        animation_props = ""
        if animations:
            initial = animations.get("initial", {})
            animate = animations.get("animate", {})
            transition = animations.get("transition", {})
            
            initial_str = ", ".join([f"{k}: {repr(v)}" for k, v in initial.items()])
            animate_str = ", ".join([f"{k}: {repr(v)}" for k, v in animate.items()])
            transition_str = ", ".join([f"{k}: {repr(v)}" for k, v in transition.items()])
            
            animation_props = f"""
      initial={{ {{ {initial_str} }} }}
      animate={{ {{ {animate_str} }} }}
      transition={{ {{ {transition_str} }} }}
"""
        
        return f"""{motion_import}import React from 'react';

export const {name} = () => {{
  return (
    <motion.div{animation_props} className="{name.lower()}">
      {name} Component
    </motion.div>
  );
}};

export default {name};
"""
