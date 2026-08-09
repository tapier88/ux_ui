"""
Motion Planner - Animation planning logic
"""
from typing import Dict, List, Optional, Any
from .models import MotionPlan, AnimationType, ResourceSource


class MotionPlanner:
    """Plans motion and animations for the design build"""
    
    def __init__(self):
        self._motion_counter = 0
    
    def _generate_id(self, prefix: str = "motion") -> str:
        """Generate unique motion ID"""
        self._motion_counter += 1
        return f"{prefix}_{self._motion_counter}"
    
    def plan_motion(
        self,
        target: str,
        trigger: str,
        animation_type: AnimationType,
        duration: str = "300ms",
        delay: str = "0ms",
        easing: str = "cubic-bezier(0.4, 0, 0.2, 1)",
        from_state: Optional[Dict[str, Any]] = None,
        to_state: Optional[Dict[str, Any]] = None,
        scrub: bool = False,
        pin: bool = False,
        stagger: Optional[float] = None,
        priority: str = "normal",
        mobile_behavior: Optional[str] = None,
        reduced_motion_behavior: Optional[str] = None,
        resource: ResourceSource = ResourceSource.MOTION
    ) -> MotionPlan:
        """Create a motion plan"""
        return MotionPlan(
            target=target,
            trigger=trigger,
            type=animation_type,
            duration=duration,
            delay=delay,
            easing=easing,
            from_state=from_state or {},
            to_state=to_state or {},
            scrub=scrub,
            pin=pin,
            stagger=stagger,
            priority=priority,
            mobile_behavior=mobile_behavior,
            reduced_motion_behavior=reduced_motion_behavior,
            resource=resource
        )
    
    def plan_fade_in(
        self,
        target: str,
        trigger: str = "load",
        duration: str = "500ms",
        stagger: Optional[float] = 0.1
    ) -> MotionPlan:
        """Plan a fade-in animation"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.FADE,
            duration=duration,
            from_state={"opacity": 0},
            to_state={"opacity": 1},
            stagger=stagger,
            reduced_motion_behavior="skip"
        )
    
    def plan_slide_in(
        self,
        target: str,
        direction: str = "up",
        trigger: str = "scroll",
        duration: str = "600ms"
    ) -> MotionPlan:
        """Plan a slide-in animation"""
        directions = {
            "up": {"y": "50px", "x": "0"},
            "down": {"y": "-50px", "x": "0"},
            "left": {"x": "50px", "y": "0"},
            "right": {"x": "-50px", "y": "0"}
        }
        from_pos = directions.get(direction, {"y": "50px", "x": "0"})
        
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.SLIDE,
            duration=duration,
            from_state={"y": from_pos["y"], "x": from_pos["x"], "opacity": 0},
            to_state={"y": "0", "x": "0", "opacity": 1},
            reduced_motion_behavior="skip"
        )
    
    def plan_scale_in(
        self,
        target: str,
        trigger: str = "load",
        duration: str = "400ms"
    ) -> MotionPlan:
        """Plan a scale-in animation"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.SCALE,
            duration=duration,
            from_state={"scale": 0.9, "opacity": 0},
            to_state={"scale": 1, "opacity": 1},
            reduced_motion_behavior="skip"
        )
    
    def plan_parallax(
        self,
        target: str,
        speed: float = 0.5,
        trigger: str = "scroll"
    ) -> MotionPlan:
        """Plan a parallax scroll effect"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.PARALLAX,
            scrub=True,
            from_state={"y": "0%"},
            to_state={"y": f"{speed * 100}%"},
            mobile_behavior="disabled",
            reduced_motion_behavior="disabled"
        )
    
    def plan_sticky_scroll(
        self,
        target: str,
        start: str = "top top",
        end: str = "bottom bottom"
    ) -> MotionPlan:
        """Plan a sticky scroll effect"""
        return self.plan_motion(
            target=target,
            trigger="scroll",
            animation_type=AnimationType.STICKY,
            pin=True,
            from_state={"position": "relative"},
            to_state={"position": "sticky"},
            mobile_behavior="static",
            reduced_motion_behavior="static"
        )
    
    def plan_scrub_animation(
        self,
        target: str,
        property_name: str,
        from_value: Any,
        to_value: Any,
        start: str = "top center",
        end: str = "bottom center"
    ) -> MotionPlan:
        """Plan a scrub-linked animation"""
        return self.plan_motion(
            target=target,
            trigger="scroll",
            animation_type=AnimationType.SCRUB,
            scrub=True,
            from_state={property_name: from_value},
            to_state={property_name: to_value},
            mobile_behavior="linear",
            reduced_motion_behavior="end-state"
        )
    
    def plan_stagger_children(
        self,
        parent_target: str,
        child_selector: str,
        stagger_amount: float = 0.1,
        trigger: str = "load"
    ) -> MotionPlan:
        """Plan staggered children animation"""
        return self.plan_motion(
            target=f"{parent_target} > {child_selector}",
            trigger=trigger,
            animation_type=AnimationType.STAGGER,
            stagger=stagger_amount,
            from_state={"opacity": 0, "y": "20px"},
            to_state={"opacity": 1, "y": "0"},
            reduced_motion_behavior="no-stagger"
        )
    
    def plan_horizontal_scroll(
        self,
        target: str,
        distance: str = "100%",
        trigger: str = "scroll"
    ) -> MotionPlan:
        """Plan horizontal scroll animation"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.HORIZONTAL,
            scrub=True,
            pin=True,
            from_state={"x": "0%"},
            to_state={"x": f"-{distance}"},
            mobile_behavior="vertical-fallback",
            reduced_motion_behavior="skip"
        )
    
    def plan_transform(
        self,
        target: str,
        transforms: Dict[str, Any],
        trigger: str = "hover",
        duration: str = "300ms"
    ) -> MotionPlan:
        """Plan a transform animation"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.TRANSFORM,
            duration=duration,
            easing="cubic-bezier(0.4, 0, 0.2, 1)",
            from_state={},
            to_state=transforms,
            reduced_motion_behavior="none"
        )
    
    def plan_reveal(
        self,
        target: str,
        direction: str = "up",
        trigger: str = "scroll",
        duration: str = "700ms"
    ) -> MotionPlan:
        """Plan a reveal animation with clip-path"""
        return self.plan_motion(
            target=target,
            trigger=trigger,
            animation_type=AnimationType.REVEAL,
            duration=duration,
            from_state={"clipPath": "inset(100% 0 0 0)"},
            to_state={"clipPath": "inset(0 0 0 0)"},
            reduced_motion_behavior="visible"
        )
    
    def select_resource(
        self,
        animation_complexity: str,
        use_gsap: bool = False,
        use_lenis: bool = False
    ) -> ResourceSource:
        """Select appropriate motion resource based on requirements"""
        if use_gsap:
            return ResourceSource.GSAP
        
        if animation_complexity == "simple":
            return ResourceSource.CUSTOM  # CSS
        
        if animation_complexity == "moderate":
            return ResourceSource.MOTION
        
        if animation_complexity == "complex":
            return ResourceSource.GSAP
        
        return ResourceSource.MOTION
