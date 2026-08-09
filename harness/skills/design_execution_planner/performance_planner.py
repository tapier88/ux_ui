"""
Performance Planner - Performance constraints planning
"""
from typing import Dict, Any, Optional
from .models import PerformancePlan


class PerformancePlanner:
    """Plans performance constraints for the design build"""
    
    def plan_performance(
        self,
        image_optimization: Optional[Dict[str, Any]] = None,
        lazy_loading: bool = True,
        code_splitting: Optional[Dict[str, Any]] = None,
        font_loading: Optional[Dict[str, Any]] = None,
        animation_budget: Optional[Dict[str, Any]] = None,
        third_party_dependencies: Optional[Dict[str, Any]] = None,
        three_d_budget: Optional[Dict[str, Any]] = None,
        video_budget: Optional[Dict[str, Any]] = None,
        bundle_budget: Optional[Dict[str, Any]] = None
    ) -> PerformancePlan:
        """Create a performance plan"""
        return PerformancePlan(
            image_optimization=image_optimization or {
                "formats": ["webp", "avif"],
                "lazy_loading": True,
                "quality": 80
            },
            lazy_loading=lazy_loading,
            code_splitting=code_splitting or {
                "strategy": "route-based",
                "prefetch": True
            },
            font_loading=font_loading or {
                "strategy": "swap",
                "preload": True
            },
            animation_budget=animation_budget or {
                "max_concurrent": 5,
                "max_duration_ms": 1000
            },
            third_party_dependencies=third_party_dependencies or {},
            three_d_budget=three_d_budget or {"enabled": False},
            video_budget=video_budget or {
                "enabled": True,
                "max_size_mb": 5,
                "autoplay_muted": True
            },
            bundle_budget=bundle_budget or {
                "max_js_kb": 300,
                "max_css_kb": 50
            }
        )
    
    def plan_standard(self) -> PerformancePlan:
        """Plan standard performance constraints"""
        return PerformancePlan(
            image_optimization={
                "formats": ["webp", "avif"],
                "lazy_loading": True,
                "quality": 80,
                "max_width": 2400,
                "responsive_images": True
            },
            lazy_loading=True,
            code_splitting={
                "strategy": "route-based",
                "prefetch": True,
                "vendor_chunk": True
            },
            font_loading={
                "strategy": "swap",
                "preload": True,
                "display": "optional"
            },
            animation_budget={
                "max_concurrent": 5,
                "max_duration_ms": 1000,
                "respect_prefers_reduced_motion": True
            },
            third_party_dependencies={
                "max_count": 10,
                "async_load": True,
                "audit_required": True
            },
            three_d_budget={"enabled": False},
            video_budget={
                "enabled": True,
                "max_size_mb": 5,
                "autoplay_muted": True,
                "lazy_load": True
            },
            bundle_budget={
                "max_js_kb": 300,
                "max_css_kb": 50,
                "treeshaking": True,
                "minification": True
            }
        )
    
    def plan_aggressive(self) -> PerformancePlan:
        """Plan aggressive performance optimization"""
        return PerformancePlan(
            image_optimization={
                "formats": ["avif", "webp"],
                "lazy_loading": True,
                "quality": 75,
                "max_width": 1920,
                "responsive_images": True,
                "blur_placeholder": True
            },
            lazy_loading=True,
            code_splitting={
                "strategy": "component-level",
                "prefetch": False,
                "vendor_chunk": True,
                "dynamic_imports": True
            },
            font_loading={
                "strategy": "optional",
                "preload": False,
                "display": "optional",
                "subset": True
            },
            animation_budget={
                "max_concurrent": 3,
                "max_duration_ms": 500,
                "respect_prefers_reduced_motion": True,
                "css_only_mobile": True
            },
            third_party_dependencies={
                "max_count": 5,
                "async_load": True,
                "audit_required": True,
                "self_host": True
            },
            three_d_budget={"enabled": False},
            video_budget={
                "enabled": False,
                "max_size_mb": 2,
                "autoplay_muted": True,
                "lazy_load": True,
                "poster_required": True
            },
            bundle_budget={
                "max_js_kb": 150,
                "max_css_kb": 30,
                "treeshaking": True,
                "minification": True,
                "compression": "brotli"
            }
        )
    
    def plan_minimal(self) -> PerformancePlan:
        """Plan minimal performance requirements"""
        return PerformancePlan(
            image_optimization={
                "formats": ["webp"],
                "lazy_loading": True,
                "quality": 80
            },
            lazy_loading=True,
            code_splitting={
                "strategy": "route-based",
                "prefetch": False
            },
            font_loading={
                "strategy": "swap",
                "preload": True
            },
            animation_budget={
                "max_concurrent": 10,
                "max_duration_ms": 2000
            },
            third_party_dependencies={},
            three_d_budget={"enabled": False},
            video_budget={
                "enabled": True,
                "max_size_mb": 10
            },
            bundle_budget={
                "max_js_kb": 500,
                "max_css_kb": 100
            }
        )
    
    def reject_technique(
        self,
        technique: str,
        reason: str,
        alternative: str = None
    ) -> Dict[str, Any]:
        """Reject a visual technique due to performance cost"""
        result = {
            "technique": technique,
            "rejected": True,
            "reason": reason
        }
        if alternative:
            result["alternative"] = alternative
        return result
    
    def evaluate_technique(
        self,
        technique: str,
        performance_impact: str
    ) -> tuple[bool, str]:
        """Evaluate if a technique is acceptable given performance constraints"""
        high_impact_techniques = [
            "full-page-video",
            "complex-3d-scene",
            "multiple-parallax-layers",
            "unoptimized-gifs"
        ]
        
        if technique in high_impact_techniques and performance_impact == "high":
            return False, f"Technique '{technique}' exceeds performance budget"
        
        if performance_impact == "critical":
            return False, f"Technique '{technique}' has critical performance impact"
        
        return True, "Technique acceptable"
