"""
Skill Registry - Skill registration and loading system
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List


@dataclass
class SkillDefinition:
    """Definition of a skill"""
    name: str
    description: str
    func: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    loaded: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "loaded": self.loaded
        }


class SkillRegistry:
    """Registry for skills"""
    
    def __init__(self):
        self._skills: Dict[str, SkillDefinition] = {}
    
    def register_skill(self, name: str, description: str,
                      func: Optional[Callable] = None,
                      **metadata) -> SkillDefinition:
        """Register a new skill"""
        skill = SkillDefinition(
            name=name,
            description=description,
            func=func,
            metadata=metadata,
            loaded=(func is not None)
        )
        self._skills[name] = skill
        return skill
    
    def load_skill(self, name: str, func: Callable) -> bool:
        """Load a skill with its implementation"""
        if name not in self._skills:
            return False
        
        self._skills[name].func = func
        self._skills[name].loaded = True
        return True
    
    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """Get a skill by name"""
        return self._skills.get(name)
    
    def list_skills(self) -> List[str]:
        """List all registered skill names"""
        return list(self._skills.keys())
    
    def execute_skill(self, name: str, *args, **kwargs) -> Any:
        """Execute a skill by name"""
        skill = self._skills.get(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found")
        
        if not skill.loaded or not skill.func:
            raise ValueError(f"Skill '{name}' is not loaded")
        
        return skill.func(*args, **kwargs)
    
    def has_skill(self, name: str) -> bool:
        """Check if a skill exists"""
        return name in self._skills
    
    def is_skill_loaded(self, name: str) -> bool:
        """Check if a skill is loaded"""
        skill = self._skills.get(name)
        return skill is not None and skill.loaded
    
    def unregister_skill(self, name: str) -> bool:
        """Unregister a skill"""
        if name in self._skills:
            del self._skills[name]
            return True
        return False
    
    def clear(self):
        """Clear all skills"""
        self._skills.clear()


# Global skill registry instance
_global_skill_registry = SkillRegistry()


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry"""
    return _global_skill_registry


def register_skill(name: str, description: str, func: Optional[Callable] = None, **kwargs):
    """Convenience function to register a skill"""
    return _global_skill_registry.register_skill(name, description, func, **kwargs)


def load_skill(name: str, func: Callable) -> bool:
    """Convenience function to load a skill"""
    return _global_skill_registry.load_skill(name, func)


# Test skill for testing
def test_skill_func(data: Any = None) -> Dict[str, Any]:
    """Test skill implementation"""
    return {
        "skill": "test-skill",
        "data": data,
        "status": "executed",
        "message": "Test skill executed successfully"
    }


# Register test skill on module load
def register_test_skill():
    """Register the test skill"""
    registry = get_skill_registry()
    
    registry.register_skill(
        name="test-skill",
        description="A test skill for validation",
        func=test_skill_func,
        category="testing",
        version="1.0.0"
    )


def register_redesign_intelligence_skill():
    """Register the redesign intelligence skill"""
    from harness.skills.redesign_intelligence import redesign_intelligence_skill
    
    registry = get_skill_registry()
    
    registry.register_skill(
        name="redesign-intelligence",
        description="Transforms WebsiteDesignProfile into RedesignStrategy",
        func=redesign_intelligence_skill,
        category="design",
        version="1.0.0"
    )


def register_seo_analysis_skill():
    """Register the SEO analysis skill"""
    from harness.skills.seo_analysis import seo_analysis_skill

    registry = get_skill_registry()

    registry.register_skill(
        name="seo-analysis",
        description="Deterministic SEO readiness analysis for design pipeline outputs",
        func=seo_analysis_skill,
        category="design",
        version="1.0.0",
    )


# Auto-register test skill
register_test_skill()

# Auto-register redesign intelligence skill
try:
    register_redesign_intelligence_skill()
except Exception:
    pass  # May fail if redesign_intelligence module has issues

# Auto-register SEO analysis skill
try:
    register_seo_analysis_skill()
except Exception:
    pass  # May fail if seo_analysis module has issues
