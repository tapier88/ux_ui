"""
Component Planner - Component planning logic
"""
from typing import Dict, List, Optional, Any
from .models import (
    ComponentPlan, ResourceSource, LayoutType, AnimationType
)


class ComponentPlanner:
    """Plans components for the design build"""
    
    def __init__(self):
        self._component_counter = 0
    
    def _generate_id(self, prefix: str = "comp") -> str:
        """Generate unique component ID"""
        self._component_counter += 1
        return f"{prefix}_{self._component_counter}"
    
    def plan_component(
        self,
        name: str,
        component_type: str,
        purpose: str,
        source_resource: ResourceSource = ResourceSource.CUSTOM,
        variants: Optional[List[str]] = None,
        props: Optional[Dict[str, Any]] = None,
        states: Optional[List[str]] = None,
        responsive_behavior: Optional[Dict[str, Any]] = None,
        accessibility: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        inspiration_source: Optional[str] = None,
        adaptation_reason: Optional[str] = None
    ) -> ComponentPlan:
        """Create a component plan"""
        return ComponentPlan(
            id=self._generate_id(),
            name=name,
            type=component_type,
            purpose=purpose,
            source_resource=source_resource,
            variants=variants or [],
            props=props or {},
            states=states or [],
            responsive_behavior=responsive_behavior or {},
            accessibility=accessibility or {},
            animation=animation,
            dependencies=dependencies or [],
            inspiration_source=inspiration_source,
            adaptation_reason=adaptation_reason
        )
    
    def plan_button(
        self,
        variant: str = "primary",
        purpose: str = "User action trigger"
    ) -> ComponentPlan:
        """Plan a button component"""
        return self.plan_component(
            name="Button",
            component_type="button",
            purpose=purpose,
            source_resource=ResourceSource.SHADCN,
            variants=["primary", "secondary", "outline", "ghost"],
            props={
                "variant": variant,
                "size": "md",
                "disabled": False
            },
            states=["default", "hover", "active", "disabled", "focus"],
            accessibility={
                "role": "button",
                "keyboard_accessible": True,
                "focus_visible": True
            }
        )
    
    def plan_card(
        self,
        purpose: str = "Content container"
    ) -> ComponentPlan:
        """Plan a card component"""
        return self.plan_component(
            name="Card",
            component_type="container",
            purpose=purpose,
            source_resource=ResourceSource.SHADCN,
            variants=["default", "elevated", "outlined"],
            props={
                "padding": "md",
                "radius": "lg"
            },
            states=["default", "hover"],
            accessibility={
                "role": "region",
                "aria_label": True
            }
        )
    
    def plan_navigation(
        self,
        purpose: str = "Site navigation"
    ) -> ComponentPlan:
        """Plan a navigation component"""
        return self.plan_component(
            name="Navigation",
            component_type="navigation",
            purpose=purpose,
            source_resource=ResourceSource.CUSTOM,
            variants=["horizontal", "vertical", "mobile"],
            props={
                "items": [],
                "logo_position": "left"
            },
            states=["default", "scrolled", "mobile_open"],
            accessibility={
                "role": "navigation",
                "aria_label": "Main navigation",
                "keyboard_accessible": True
            }
        )
    
    def plan_hero(
        self,
        layout: LayoutType = LayoutType.SPLIT,
        purpose: str = "Above the fold content"
    ) -> ComponentPlan:
        """Plan a hero section component"""
        return self.plan_component(
            name="Hero",
            component_type="section",
            purpose=purpose,
            source_resource=ResourceSource.CUSTOM,
            variants=["split", "centered", "full_bleed"],
            props={
                "layout": layout.value,
                "show_cta": True,
                "show_image": True
            },
            states=["default", "loaded"],
            animation="fade-in",
            accessibility={
                "role": "banner",
                "heading_level": 1
            }
        )
    
    def plan_testimonial(
        self,
        purpose: str = "Social proof display"
    ) -> ComponentPlan:
        """Plan a testimonial component"""
        return self.plan_component(
            name="Testimonial",
            component_type="content",
            purpose=purpose,
            source_resource=ResourceSource.REACT_BITS,
            inspiration_source="react-bits/testimonials",
            adaptation_reason="Adapted for brand consistency",
            variants=["single", "carousel", "grid"],
            props={
                "show_avatar": True,
                "show_rating": True
            },
            accessibility={
                "role": "blockquote",
                "aria_label": "Customer testimonial"
            }
        )
    
    def plan_form(
        self,
        form_type: str = "contact",
        purpose: str = "User input collection"
    ) -> ComponentPlan:
        """Plan a form component"""
        return self.plan_component(
            name="Form",
            component_type="form",
            purpose=purpose,
            source_resource=ResourceSource.CUSTOM,
            variants=[form_type],
            props={
                "fields": [],
                "validation": "client-side",
                "submit_method": "POST"
            },
            states=["default", "validating", "submitting", "success", "error"],
            accessibility={
                "role": "form",
                "aria_labelledby": True,
                "error_announcement": True,
                "label_association": True
            }
        )
    
    def from_design_recommendation(
        self,
        recommendation: Dict[str, Any]
    ) -> ComponentPlan:
        """Create component plan from design recommendation"""
        component_name = recommendation.get("component", "CustomComponent")
        component_type = recommendation.get("type", "custom")
        purpose = recommendation.get("purpose", "Custom component")
        
        # Determine source resource
        source_str = recommendation.get("source", "custom")
        source_map = {
            "react-bits": ResourceSource.REACT_BITS,
            "shadcn": ResourceSource.SHADCN,
            "motion": ResourceSource.MOTION,
            "gsap": ResourceSource.GSAP,
            "custom": ResourceSource.CUSTOM
        }
        source_resource = source_map.get(source_str, ResourceSource.CUSTOM)
        
        return self.plan_component(
            name=component_name,
            component_type=component_type,
            purpose=purpose,
            source_resource=source_resource,
            variants=recommendation.get("variants", []),
            props=recommendation.get("props", {}),
            states=recommendation.get("states", ["default"]),
            accessibility=recommendation.get("accessibility", {}),
            animation=recommendation.get("animation"),
            inspiration_source=recommendation.get("inspiration_source"),
            adaptation_reason=recommendation.get("adaptation_reason")
        )
