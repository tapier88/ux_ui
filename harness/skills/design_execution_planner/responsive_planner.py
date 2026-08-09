"""
Responsive Planner - Responsive behavior planning
"""
from typing import Dict, Optional, Any
from .models import ResponsivePlan, ResponsiveBehavior


class ResponsivePlanner:
    """Plans responsive behavior for the design build"""
    
    def plan_responsive(
        self,
        desktop: Optional[Dict[str, Any]] = None,
        tablet: Optional[Dict[str, Any]] = None,
        mobile: Optional[Dict[str, Any]] = None
    ) -> ResponsivePlan:
        """Create a responsive plan"""
        return ResponsivePlan(
            desktop=self._create_behavior(desktop or {}),
            tablet=self._create_behavior(tablet or {}),
            mobile=self._create_behavior(mobile or {})
        )
    
    def _create_behavior(self, config: Dict[str, Any]) -> ResponsiveBehavior:
        """Create a responsive behavior from config"""
        return ResponsiveBehavior(
            layout_change=config.get("layout_change"),
            font_change=config.get("font_change"),
            spacing_change=config.get("spacing_change"),
            image_change=config.get("image_change"),
            animation_change=config.get("animation_change"),
            visibility_change=config.get("visibility_change", False),
            interaction_change=config.get("interaction_change")
        )
    
    def plan_standard_responsive(self) -> ResponsivePlan:
        """Plan standard responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change=None,
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            tablet=ResponsiveBehavior(
                layout_change="stack-columns",
                font_change={"scale": 0.9},
                spacing_change={"reduce": "20%"},
                image_change={"resize": "medium"},
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            mobile=ResponsiveBehavior(
                layout_change="single-column",
                font_change={"scale": 0.85},
                spacing_change={"reduce": "40%"},
                image_change={"resize": "small", "crop": "center"},
                animation_change="simplified",
                visibility_change=False,
                interaction_change="touch-optimized"
            )
        )
    
    def plan_hero_responsive(self) -> ResponsivePlan:
        """Plan hero section responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change=None,
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change="full",
                visibility_change=False,
                interaction_change=None
            ),
            tablet=ResponsiveBehavior(
                layout_change="vertical-stack",
                font_change={"h1": "2.5rem", "h2": "1.75rem"},
                spacing_change={"padding": "3rem"},
                image_change={"height": "400px"},
                animation_change="reduced",
                visibility_change=False,
                interaction_change=None
            ),
            mobile=ResponsiveBehavior(
                layout_change="full-width-stack",
                font_change={"h1": "2rem", "h2": "1.5rem"},
                spacing_change={"padding": "2rem"},
                image_change={"height": "250px", "object_fit": "cover"},
                animation_change="minimal",
                visibility_change=False,
                interaction_change="tap-only"
            )
        )
    
    def plan_navigation_responsive(self) -> ResponsivePlan:
        """Plan navigation responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change="horizontal",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change="hover"
            ),
            tablet=ResponsiveBehavior(
                layout_change="condensed-horizontal",
                font_change={"scale": 0.9},
                spacing_change={"gap": "1rem"},
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change="hover"
            ),
            mobile=ResponsiveBehavior(
                layout_change="hamburger-menu",
                font_change={"scale": 1},
                spacing_change={"padding": "1rem"},
                image_change={"logo_size": "small"},
                animation_change="slide-in",
                visibility_change=False,
                interaction_change="tap-toggle"
            )
        )
    
    def plan_grid_responsive(self, columns_desktop: int = 4) -> ResponsivePlan:
        """Plan grid layout responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change=f"grid-{columns_desktop}-cols",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            tablet=ResponsiveBehavior(
                layout_change=f"grid-{max(2, columns_desktop // 2)}-cols",
                font_change=None,
                spacing_change={"gap": "1rem"},
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            mobile=ResponsiveBehavior(
                layout_change="grid-1-col",
                font_change=None,
                spacing_change={"gap": "0.75rem"},
                image_change={"aspect_ratio": "1:1"},
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            )
        )
    
    def plan_content_responsive(self) -> ResponsivePlan:
        """Plan content section responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change="side-by-side",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change="fade-in",
                visibility_change=False,
                interaction_change=None
            ),
            tablet=ResponsiveBehavior(
                layout_change="stacked",
                font_change={"body": "0.95rem"},
                spacing_change={"margin": "2rem"},
                image_change={"width": "100%"},
                animation_change="fade-in",
                visibility_change=False,
                interaction_change=None
            ),
            mobile=ResponsiveBehavior(
                layout_change="full-width-stacked",
                font_change={"body": "1rem", "line_height": "1.7"},
                spacing_change={"margin": "1rem"},
                image_change={"width": "100%", "loading": "lazy"},
                animation_change="none",
                visibility_change=False,
                interaction_change="scroll-native"
            )
        )
    
    def plan_sidebar_responsive(self) -> ResponsivePlan:
        """Plan sidebar responsive behavior"""
        return ResponsivePlan(
            desktop=ResponsiveBehavior(
                layout_change="sidebar-right",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            tablet=ResponsiveBehavior(
                layout_change="sidebar-below",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change=None,
                visibility_change=False,
                interaction_change=None
            ),
            mobile=ResponsiveBehavior(
                layout_change="hidden-drawer",
                font_change=None,
                spacing_change=None,
                image_change=None,
                animation_change="slide-in",
                visibility_change=True,
                interaction_change="drawer-toggle"
            )
        )
