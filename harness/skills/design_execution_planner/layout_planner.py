"""
Layout Planner - Layout specifications
"""
from typing import Dict, List, Optional, Any
from .models import LayoutPlan, LayoutType


class LayoutPlanner:
    """Plans layout specifications for the design build"""
    
    def __init__(self):
        self._default_layouts = {
            LayoutType.STANDARD: self._standard_layout,
            LayoutType.SPLIT: self._split_layout,
            LayoutType.CENTERED: self._centered_layout,
            LayoutType.FULL_BLEED: self._full_bleed_layout,
            LayoutType.ASYMMETRIC: self._asymmetric_layout,
            LayoutType.EDITORIAL: self._editorial_layout,
            LayoutType.OVERLAPPING: self._overlapping_layout,
            LayoutType.IMMERSIVE: self._immersive_layout,
            LayoutType.BENTO: self._bento_layout,
            LayoutType.LAYERED: self._layered_layout,
            LayoutType.DIAGONAL: self._diagonal_layout,
            LayoutType.STORYTELLING: self._storytelling_layout,
            LayoutType.EXPERIMENTAL: self._experimental_layout,
            LayoutType.GRID: self._grid_layout,
            LayoutType.HORIZONTAL: self._horizontal_layout,
            LayoutType.STICKY: self._sticky_layout,
        }
    
    def plan_layout(
        self,
        layout_type: LayoutType = LayoutType.STANDARD,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> LayoutPlan:
        """Create a layout plan based on type"""
        generator = self._default_layouts.get(layout_type, self._standard_layout)
        base_plan = generator()
        
        # Apply custom overrides
        if custom_settings:
            for key, value in custom_settings.items():
                if hasattr(base_plan, key):
                    setattr(base_plan, key, value)
        
        return base_plan
    
    def _standard_layout(self) -> LayoutPlan:
        """Standard centered container layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="12-column",
            columns=12,
            gaps={"row": "1.5rem", "col": "1.5rem"},
            alignment="center",
            positioning="relative",
            image_position="right",
            text_position="left",
            content_density="normal",
            white_space="generous"
        )
    
    def _split_layout(self) -> LayoutPlan:
        """Split layout with text and image sides"""
        return LayoutPlan(
            container_width="1400px",
            grid="12-column",
            columns=12,
            gaps={"row": "2rem", "col": "3rem"},
            alignment="center",
            positioning="relative",
            layering=["text-content", "image-content"],
            overlap=False,
            z_index={"text-content": 1, "image-content": 1},
            image_position="right",
            text_position="left",
            content_density="normal",
            white_space="generous"
        )
    
    def _centered_layout(self) -> LayoutPlan:
        """Centered content layout"""
        return LayoutPlan(
            container_width="800px",
            grid="single-column",
            columns=1,
            gaps={"row": "1rem", "col": "0"},
            alignment="center",
            positioning="relative",
            image_position="center",
            text_position="center",
            content_density="normal",
            white_space="generous"
        )
    
    def _full_bleed_layout(self) -> LayoutPlan:
        """Full viewport width layout"""
        return LayoutPlan(
            container_width="100vw",
            grid="12-column",
            columns=12,
            gaps={"row": "0", "col": "0"},
            alignment="stretch",
            positioning="relative",
            image_position="full",
            text_position="overlay",
            content_density="dense",
            white_space="minimal"
        )
    
    def _asymmetric_layout(self) -> LayoutPlan:
        """Asymmetric grid layout"""
        return LayoutPlan(
            container_width="1400px",
            grid="asymmetric-12",
            columns=12,
            gaps={"row": "2rem", "col": "2rem"},
            alignment="left",
            positioning="relative",
            layering=["background", "primary", "secondary", "accent"],
            overlap=True,
            z_index={"background": 0, "primary": 1, "secondary": 2, "accent": 3},
            image_position="span-7",
            text_position="span-5",
            content_density="dense",
            white_space="normal"
        )
    
    def _editorial_layout(self) -> LayoutPlan:
        """Editorial/magazine style layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="editorial",
            columns=12,
            gaps={"row": "3rem", "col": "2rem"},
            alignment="left",
            positioning="relative",
            layering=["headline", "content", "sidebar"],
            overlap=False,
            z_index={"headline": 2, "content": 1, "sidebar": 1},
            image_position="featured",
            text_position="flow",
            content_density="varied",
            white_space="generous"
        )
    
    def _overlapping_layout(self) -> LayoutPlan:
        """Overlapping elements layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="12-column",
            columns=12,
            gaps={"row": "1rem", "col": "1rem"},
            alignment="center",
            positioning="absolute",
            layering=["background", "midground", "foreground"],
            overlap=True,
            z_index={"background": 0, "midground": 1, "foreground": 2},
            image_position="overlap-text",
            text_position="overlap-image",
            content_density="dense",
            white_space="minimal"
        )
    
    def _immersive_layout(self) -> LayoutPlan:
        """Immersive full-screen layout"""
        return LayoutPlan(
            container_width="100vw",
            grid="viewport",
            columns=1,
            gaps={"row": "0", "col": "0"},
            alignment="center",
            positioning="fixed",
            layering=["background-media", "overlay", "content"],
            overlap=True,
            z_index={"background-media": 0, "overlay": 1, "content": 2},
            image_position="background",
            text_position="center-overlay",
            content_density="sparse",
            white_space="generous"
        )
    
    def _bento_layout(self) -> LayoutPlan:
        """Bento box grid layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="bento",
            columns=6,
            gaps={"row": "1rem", "col": "1rem"},
            alignment="stretch",
            positioning="relative",
            layering=["box-1", "box-2", "box-3", "box-4"],
            overlap=False,
            z_index={f"box-{i}": 1 for i in range(1, 5)},
            image_position="varies",
            text_position="varies",
            content_density="varied",
            white_space="normal"
        )
    
    def _layered_layout(self) -> LayoutPlan:
        """Multi-layer depth layout"""
        return LayoutPlan(
            container_width="1400px",
            grid="12-column",
            columns=12,
            gaps={"row": "2rem", "col": "2rem"},
            alignment="center",
            positioning="relative",
            layering=["base", "layer-1", "layer-2", "layer-3", "floating"],
            overlap=True,
            z_index={"base": 0, "layer-1": 1, "layer-2": 2, "layer-3": 3, "floating": 4},
            image_position="layered",
            text_position="layered",
            content_density="dense",
            white_space="normal"
        )
    
    def _diagonal_layout(self) -> LayoutPlan:
        """Diagonal composition layout"""
        return LayoutPlan(
            container_width="1400px",
            grid="diagonal",
            columns=12,
            gaps={"row": "2rem", "col": "2rem"},
            alignment="diagonal",
            positioning="relative",
            layering=["bottom-left", "center", "top-right"],
            overlap=True,
            z_index={"bottom-left": 1, "center": 2, "top-right": 3},
            image_position="diagonal-flow",
            text_position="diagonal-flow",
            content_density="varied",
            white_space="generous"
        )
    
    def _storytelling_layout(self) -> LayoutPlan:
        """Scroll-based storytelling layout"""
        return LayoutPlan(
            container_width="100%",
            grid="vertical-flow",
            columns=1,
            gaps={"row": "0", "col": "0"},
            alignment="center",
            positioning="sticky",
            layering=["scene-1", "scene-2", "scene-3", "scene-4"],
            overlap=False,
            z_index={f"scene-{i}": i for i in range(1, 5)},
            image_position="scroll-driven",
            text_position="scroll-driven",
            content_density="varied",
            white_space="generous"
        )
    
    def _experimental_layout(self) -> LayoutPlan:
        """Experimental/avant-garde layout"""
        return LayoutPlan(
            container_width="100vw",
            grid="free-form",
            columns=12,
            gaps={"row": "varies", "col": "varies"},
            alignment="dynamic",
            positioning="absolute",
            layering=["element-1", "element-2", "element-3"],
            overlap=True,
            z_index={"element-1": 1, "element-2": 2, "element-3": 3},
            image_position="unconventional",
            text_position="unconventional",
            content_density="varied",
            white_space="dynamic"
        )
    
    def _grid_layout(self) -> LayoutPlan:
        """Strict grid layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="strict-12",
            columns=12,
            gaps={"row": "1.5rem", "col": "1.5rem"},
            alignment="stretch",
            positioning="relative",
            layering=["grid-cell"],
            overlap=False,
            image_position="grid-aligned",
            text_position="grid-aligned",
            content_density="normal",
            white_space="normal"
        )
    
    def _horizontal_layout(self) -> LayoutPlan:
        """Horizontal scrolling layout"""
        return LayoutPlan(
            container_width="100vw",
            grid="horizontal-flow",
            columns=1,
            gaps={"row": "0", "col": "2rem"},
            alignment="center",
            positioning="relative",
            layering=["slide-1", "slide-2", "slide-3"],
            overlap=False,
            image_position="horizontal-center",
            text_position="horizontal-center",
            content_density="sparse",
            white_space="generous"
        )
    
    def _sticky_layout(self) -> LayoutPlan:
        """Sticky section layout"""
        return LayoutPlan(
            container_width="1200px",
            grid="12-column",
            columns=12,
            gaps={"row": "0", "col": "2rem"},
            alignment="center",
            positioning="sticky",
            layering=["sticky-section", "scrolling-content"],
            overlap=False,
            z_index={"sticky-section": 10, "scrolling-content": 1},
            image_position="sticky-side",
            text_position="scrolling-main",
            content_density="normal",
            white_space="generous"
        )
