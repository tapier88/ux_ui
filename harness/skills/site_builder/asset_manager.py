"""
Asset Manager - Asset handling and Higgsfield abstraction
"""
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import GenerationTask


class AssetManager:
    """Manages assets including Higgsfield generation abstraction"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.assets_added: List[str] = []
        self.generation_tasks: List[GenerationTask] = []
    
    def classify_asset(self, asset_info: Dict[str, Any]) -> str:
        """Classify an asset as existing, generated, external, placeholder, or missing"""
        if asset_info.get("existing", False):
            return "existing"
        elif asset_info.get("generation_required", False):
            return "generated"
        elif asset_info.get("external_url"):
            return "external"
        elif asset_info.get("placeholder", False):
            return "placeholder"
        else:
            return "missing"
    
    def add_existing_asset(self, source_path: str, dest_path: str) -> str:
        """Add an existing asset from the project"""
        source_full = self.project_path / source_path
        
        if not source_full.exists():
            raise FileNotFoundError(f"Asset not found: {source_path}")
        
        # Copy to destination
        dest_full = self.project_path / dest_path
        dest_full.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(source_full, dest_full)
        
        self.assets_added.append(dest_path)
        return dest_path
    
    def add_external_asset(self, url: str, dest_path: str) -> str:
        """Register an external asset URL"""
        # For external assets, we just record the path
        # The actual download would happen at build time or runtime
        self.assets_added.append(dest_path)
        return dest_path
    
    def create_placeholder(self, width: int, height: int, 
                          dest_path: str, alt: str = "") -> str:
        """Create a placeholder asset"""
        dest_full = self.project_path / dest_path
        dest_full.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a simple SVG placeholder
        svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="#e5e7eb"/>
  <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="14" fill="#6b7280">
    {alt or f"{width}x{height}"}
  </text>
</svg>'''
        
        with open(dest_full, 'w') as f:
            f.write(svg_content)
        
        self.assets_added.append(dest_path)
        return dest_path
    
    def queue_generation_task(self, task: GenerationTask) -> str:
        """Queue an asset generation task (Higgsfield abstraction)"""
        self.generation_tasks.append(task)
        return task.task_id
    
    def process_asset_plan(self, asset_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Process an AssetPlan and handle assets accordingly"""
        assets = asset_plan.get("assets", [])
        results = {"processed": [], "pending_generation": [], "errors": []}
        
        for asset in assets:
            classification = self.classify_asset(asset)
            
            try:
                if classification == "existing":
                    source = asset.get("source")
                    dest = asset.get("dest")
                    path = self.add_existing_asset(source, dest)
                    results["processed"].append({
                        "type": "existing",
                        "path": path,
                    })
                
                elif classification == "external":
                    url = asset.get("external_url")
                    dest = asset.get("dest")
                    path = self.add_external_asset(url, dest)
                    results["processed"].append({
                        "type": "external",
                        "url": url,
                        "path": path,
                    })
                
                elif classification == "placeholder":
                    width = asset.get("width", 800)
                    height = asset.get("height", 600)
                    dest = asset.get("dest")
                    alt = asset.get("alt", "Placeholder")
                    path = self.create_placeholder(width, height, dest, alt)
                    results["processed"].append({
                        "type": "placeholder",
                        "path": path,
                    })
                
                elif classification == "generated":
                    # Create GenerationTask for Higgsfield
                    generator = asset.get("generator", "higgsfield")
                    
                    task = GenerationTask(
                        task_id=f"gen_{len(self.generation_tasks)}",
                        generator=generator,
                        asset_type=asset.get("asset_type", "image"),
                        creative_direction=asset.get("creative_direction", ""),
                        style=asset.get("style", ""),
                        composition=asset.get("composition", ""),
                        aspect_ratio=asset.get("aspect_ratio", "16:9"),
                        purpose=asset.get("purpose", ""),
                        status="pending",
                        metadata=asset.get("metadata", {}),
                    )
                    
                    task_id = self.queue_generation_task(task)
                    results["pending_generation"].append({
                        "type": "generated",
                        "task_id": task_id,
                        "generator": generator,
                    })
                
                elif classification == "missing":
                    # Create placeholder for missing assets
                    dest = asset.get("dest", f"assets/missing_{len(self.assets_added)}.svg")
                    path = self.create_placeholder(800, 600, dest, "Missing Asset")
                    results["processed"].append({
                        "type": "missing_replaced",
                        "path": path,
                    })
            
            except Exception as e:
                results["errors"].append({
                    "asset": asset,
                    "error": str(e),
                })
        
        return results
    
    def get_assets_added(self) -> List[str]:
        """Get list of added asset paths"""
        return self.assets_added
    
    def get_generation_tasks(self) -> List[GenerationTask]:
        """Get pending generation tasks"""
        return self.generation_tasks
    
    def optimize_image(self, image_path: str, 
                      output_format: str = "webp",
                      quality: int = 80) -> str:
        """Optimize an image (abstraction - real implementation would use image processing)"""
        # This is an abstraction - real implementation would:
        # 1. Load the image
        # 2. Resize if needed
        # 3. Convert to WebP/AVIF
        # 4. Apply compression
        # 5. Save optimized version
        
        input_path = self.project_path / image_path
        
        if not input_path.exists():
            return image_path
        
        # Generate output path
        output_name = f"{input_path.stem}.{output_format}"
        output_path = input_path.parent / output_name
        
        # For now, just return the original path
        # Real implementation would do actual optimization
        return str(output_path.relative_to(self.project_path))
