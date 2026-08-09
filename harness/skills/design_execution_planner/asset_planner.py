"""
Asset Planner - Asset requirements planning
"""
from typing import Dict, List, Optional, Any
from .models import AssetPlan, AssetType, GenerationRequest


class AssetPlanner:
    """Plans assets for the design build"""
    
    def __init__(self):
        self._asset_counter = 0
    
    def _generate_id(self, prefix: str = "asset") -> str:
        """Generate unique asset ID"""
        self._asset_counter += 1
        return f"{prefix}_{self._asset_counter}"
    
    def plan_asset(
        self,
        asset_type: AssetType,
        purpose: str,
        source: Optional[str] = None,
        generation_required: bool = False,
        generator: Optional[str] = None,
        dimensions: Optional[Dict[str, int]] = None,
        aspect_ratio: Optional[str] = None,
        format: str = "webp",
        priority: str = "normal",
        optimization: Optional[Dict[str, Any]] = None,
        generation_request: Optional[GenerationRequest] = None
    ) -> AssetPlan:
        """Create an asset plan"""
        return AssetPlan(
            id=self._generate_id(),
            type=asset_type,
            purpose=purpose,
            source=source,
            generation_required=generation_required,
            generator=generator,
            dimensions=dimensions,
            aspect_ratio=aspect_ratio,
            format=format,
            priority=priority,
            optimization=optimization or {},
            generation_request=generation_request
        )
    
    def plan_image(
        self,
        purpose: str,
        width: int = 1200,
        height: int = 800,
        source: Optional[str] = None,
        generation_required: bool = False
    ) -> AssetPlan:
        """Plan an image asset"""
        return self.plan_asset(
            asset_type=AssetType.IMAGE,
            purpose=purpose,
            source=source,
            generation_required=generation_required,
            generator="higgsfield" if generation_required else None,
            dimensions={"width": width, "height": height},
            aspect_ratio=f"{width}:{height}",
            format="webp",
            optimization={
                "formats": ["webp", "avif"],
                "quality": 80,
                "lazy_loading": True
            }
        )
    
    def plan_hero_image(
        self,
        source: Optional[str] = None,
        generation_required: bool = False,
        creative_direction: Optional[str] = None
    ) -> AssetPlan:
        """Plan a hero image asset"""
        gen_request = None
        if generation_required and creative_direction:
            gen_request = GenerationRequest(
                asset_type="image",
                creative_direction=creative_direction,
                composition="hero-centered",
                style="professional",
                aspect_ratio="16:9",
                resolution="1920x1080",
                purpose="Hero section background"
            )
        
        return self.plan_asset(
            asset_type=AssetType.IMAGE,
            purpose="Hero section visual",
            source=source,
            generation_required=generation_required,
            generator="higgsfield" if generation_required else None,
            dimensions={"width": 1920, "height": 1080},
            aspect_ratio="16:9",
            format="webp",
            priority="critical",
            optimization={
                "formats": ["webp", "avif"],
                "quality": 85,
                "lazy_loading": False,
                "preload": True
            },
            generation_request=gen_request
        )
    
    def plan_illustration(
        self,
        purpose: str,
        style: str = "modern",
        dimensions: Optional[Dict[str, int]] = None
    ) -> AssetPlan:
        """Plan an illustration asset"""
        return self.plan_asset(
            asset_type=AssetType.ILLUSTRATION,
            purpose=purpose,
            generation_required=True,
            generator="higgsfield",
            dimensions=dimensions or {"width": 800, "height": 600},
            aspect_ratio="4:3",
            format="svg",
            priority="normal",
            optimization={
                "optimize_svg": True,
                "remove_metadata": True
            },
            generation_request=GenerationRequest(
                asset_type="illustration",
                creative_direction=f"{style} style illustration",
                composition="balanced",
                style=style,
                aspect_ratio="4:3",
                resolution="800x600",
                purpose=purpose
            )
        )
    
    def plan_icon(
        self,
        purpose: str,
        icon_set: str = "lucide",
        size: int = 24
    ) -> AssetPlan:
        """Plan an icon asset"""
        return self.plan_asset(
            asset_type=AssetType.ICON,
            purpose=purpose,
            source=icon_set,
            dimensions={"width": size, "height": size},
            aspect_ratio="1:1",
            format="svg",
            priority="normal",
            optimization={
                "sprite_sheet": True,
                "inline_svg": True
            }
        )
    
    def plan_video(
        self,
        purpose: str,
        duration_seconds: int = 30,
        autoplay: bool = False,
        muted: bool = True
    ) -> AssetPlan:
        """Plan a video asset"""
        return self.plan_asset(
            asset_type=AssetType.VIDEO,
            purpose=purpose,
            generation_required=False,
            dimensions={"width": 1920, "height": 1080},
            aspect_ratio="16:9",
            format="mp4",
            priority="high",
            optimization={
                "formats": ["mp4", "webm"],
                "max_size_mb": 5,
                "autoplay": autoplay,
                "muted": muted,
                "loop": True,
                "preload": "metadata"
            }
        )
    
    def plan_background(
        self,
        purpose: str,
        bg_type: str = "gradient",
        generation_required: bool = False
    ) -> AssetPlan:
        """Plan a background asset"""
        return self.plan_asset(
            asset_type=AssetType.BACKGROUND,
            purpose=purpose,
            generation_required=generation_required,
            generator="higgsfield" if generation_required else None,
            format="webp" if not generation_required else "css",
            priority="normal",
            optimization={
                "tileable": bg_type == "texture",
                "css_fallback": True
            }
        )
    
    def plan_logo(
        self,
        purpose: str = "Brand logo",
        variants: List[str] = None
    ) -> AssetPlan:
        """Plan a logo asset"""
        variants = variants or ["light", "dark", "icon"]
        return self.plan_asset(
            asset_type=AssetType.LOGO,
            purpose=purpose,
            format="svg",
            priority="critical",
            optimization={
                "sprite_sheet": False,
                "inline_svg": True,
                "variants": variants
            }
        )
    
    def plan_texture(
        self,
        purpose: str,
        tileable: bool = True,
        generation_required: bool = True
    ) -> AssetPlan:
        """Plan a texture asset"""
        return self.plan_asset(
            asset_type=AssetType.TEXTURE,
            purpose=purpose,
            generation_required=generation_required,
            generator="higgsfield",
            format="webp",
            priority="low",
            optimization={
                "tileable": tileable,
                "seamless": True,
                "compression": "high"
            },
            generation_request=GenerationRequest(
                asset_type="texture",
                creative_direction="subtle texture pattern",
                composition="seamless",
                style="minimal",
                aspect_ratio="1:1",
                resolution="512x512",
                purpose=purpose
            )
        )
    
    def plan_3d_asset(
        self,
        purpose: str,
        format: str = "gltf",
        max_polygons: int = 10000
    ) -> AssetPlan:
        """Plan a 3D asset"""
        return self.plan_asset(
            asset_type=AssetType.THREE_D,
            purpose=purpose,
            format=format,
            priority="high",
            optimization={
                "max_polygons": max_polygons,
                "compressed_textures": True,
                "lod_levels": 3
            }
        )
    
    def from_design_resource_report(
        self,
        resource_report: Dict[str, Any]
    ) -> List[AssetPlan]:
        """Create asset plans from design resource report"""
        assets = []
        required_assets = resource_report.get("required_assets", [])
        
        for asset_spec in required_assets:
            asset_type_str = asset_spec.get("type", "image")
            asset_type = getattr(AssetType, asset_type_str.upper(), AssetType.IMAGE)
            
            plan = self.plan_asset(
                asset_type=asset_type,
                purpose=asset_spec.get("purpose", "Generic asset"),
                source=asset_spec.get("source"),
                generation_required=asset_spec.get("generation_required", False),
                generator=asset_spec.get("generator"),
                dimensions=asset_spec.get("dimensions"),
                aspect_ratio=asset_spec.get("aspect_ratio"),
                priority=asset_spec.get("priority", "normal")
            )
            assets.append(plan)
        
        return assets
