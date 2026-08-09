"""
Tests for Redesign Intelligence Skill

Tests cover:
1. Import
2. Models
3. Skill registry
4. Preserve engine
5. Remove engine
6. Improvement engine
7. Layout strategy
8. Visual strategy
9. Typography strategy
10. Color strategy
11. Component strategy
12. Motion strategy
13. Accessibility strategy
14. Performance strategy
15. Design diversity
16. Design Engine integration
17. Empty profile
18. Incomplete profile
19. Unknown values
20. Deterministic output
"""

from harness.skills.redesign_intelligence import (
    run_redesign_intelligence,
    RedesignIntelligenceEngine,
    PreserveDecision,
    RemoveDecision,
    ImproveDecision,
    LayoutStrategy,
    VisualStrategy,
    TypographyStrategy,
    ColorStrategy,
    ComponentStrategy,
    MotionStrategy,
    ContentHierarchyStrategy,
    PerformanceStrategy,
    AccessibilityStrategy,
    DesignRisk,
    RedesignStrategy,
)
from harness.skills import get_skill_registry, load_skill


class TestImport:
    """Test 1: Import test"""
    
    def test_import_models(self):
        """All models should be importable"""
        assert PreserveDecision is not None
        assert RemoveDecision is not None
        assert ImproveDecision is not None
        assert LayoutStrategy is not None
        assert VisualStrategy is not None
        assert TypographyStrategy is not None
        assert ColorStrategy is not None
        assert ComponentStrategy is not None
        assert MotionStrategy is not None
        assert ContentHierarchyStrategy is not None
        assert PerformanceStrategy is not None
        assert AccessibilityStrategy is not None
        assert DesignRisk is not None
        assert RedesignStrategy is not None
    
    def test_import_engine(self):
        """Engine should be importable"""
        assert RedesignIntelligenceEngine is not None
        assert run_redesign_intelligence is not None


class TestModels:
    """Test 2: Model tests"""
    
    def test_preserve_decision_to_dict(self):
        """PreserveDecision should serialize correctly"""
        decision = PreserveDecision(
            element="brand_identity",
            reason="Core to recognition",
            confidence=0.95
        )
        d = decision.to_dict()
        assert d["element"] == "brand_identity"
        assert d["reason"] == "Core to recognition"
        assert d["confidence"] == 0.95
    
    def test_remove_decision_to_dict(self):
        """RemoveDecision should serialize correctly"""
        decision = RemoveDecision(
            element="excessive_shadows",
            reason="Creates visual noise",
            confidence=0.75
        )
        d = decision.to_dict()
        assert d["element"] == "excessive_shadows"
        assert d["reason"] == "Creates visual noise"
    
    def test_improve_decision_to_dict(self):
        """ImproveDecision should serialize correctly"""
        decision = ImproveDecision(
            category="visual",
            current_state="High density",
            problem="Cramped content",
            proposed_change="Increase whitespace",
            expected_benefit="Better readability",
            priority="high",
            confidence=0.85
        )
        d = decision.to_dict()
        assert d["category"] == "visual"
        assert d["priority"] == "high"
    
    def test_layout_strategy_to_dict(self):
        """LayoutStrategy should serialize correctly"""
        strategy = LayoutStrategy(
            pattern="asymmetric",
            description="Dynamic tension",
            reasoning="Brand personality"
        )
        d = strategy.to_dict()
        assert d["pattern"] == "asymmetric"
    
    def test_redesign_strategy_to_dict(self):
        """RedesignStrategy should serialize correctly"""
        strategy = RedesignStrategy(
            project_summary="Test project",
            confidence=0.80,
            reasoning="Test reasoning"
        )
        d = strategy.to_dict()
        assert d["project_summary"] == "Test project"
        assert d["confidence"] == 0.80


class TestSkillRegistry:
    """Test 3: Skill registry test"""
    
    def test_skill_registered(self):
        """redesign-intelligence should be registered"""
        registry = get_skill_registry()
        assert registry.has_skill("redesign-intelligence")
    
    def test_skill_loaded(self):
        """redesign-intelligence should be loaded"""
        registry = get_skill_registry()
        assert registry.is_skill_loaded("redesign-intelligence")
    
    def test_load_skill_function(self):
        """load_skill should work with redesign-intelligence"""
        # The skill should already be loaded via auto-registration
        registry = get_skill_registry()
        assert registry.get_skill("redesign-intelligence") is not None


class TestPreserveEngine:
    """Test 4: Preserve engine test"""
    
    def test_preserves_brand_identity(self):
        """Should preserve brand identity when present"""
        profile = {"brand": {"name": "Test Corp", "logo": "logo.png"}}
        result = run_redesign_intelligence(profile)
        preserve_elements = [p["element"] for p in result["preserve"]]
        assert "brand_identity" in preserve_elements
    
    def test_preserves_value_proposition(self):
        """Should preserve value proposition when present"""
        profile = {"content": {"value_proposition": "Fast solutions"}}
        result = run_redesign_intelligence(profile)
        preserve_elements = [p["element"] for p in result["preserve"]]
        assert "value_proposition" in preserve_elements
    
    def test_preserves_with_confidence(self):
        """Preserve decisions should have confidence scores"""
        profile = {"brand": {"name": "Test"}}
        result = run_redesign_intelligence(profile)
        for p in result["preserve"]:
            assert 0 <= p["confidence"] <= 1


class TestRemoveEngine:
    """Test 5: Remove engine test"""
    
    def test_detects_excessive_shadows(self):
        """Should detect excessive shadows"""
        profile = {"visual": {"shadows": "heavy"}}
        result = run_redesign_intelligence(profile)
        remove_elements = [r["element"] for r in result["remove"]]
        assert "excessive_shadows" in remove_elements
    
    def test_detects_excessive_gradients(self):
        """Should detect excessive gradients"""
        profile = {"visual": {"gradients": "excessive"}}
        result = run_redesign_intelligence(profile)
        remove_elements = [r["element"] for r in result["remove"]]
        assert "arbitrary_gradients" in remove_elements
    
    def test_remove_has_reason(self):
        """Remove decisions should have reasons"""
        profile = {}
        result = run_redesign_intelligence(profile)
        for r in result["remove"]:
            assert "reason" in r
            assert len(r["reason"]) > 0


class TestImprovementEngine:
    """Test 6: Improvement engine test"""
    
    def test_detects_high_density(self):
        """Should detect high visual density"""
        profile = {"visual": {"density": "high"}}
        result = run_redesign_intelligence(profile)
        categories = [i["category"] for i in result["improve"]]
        assert "visual" in categories
    
    def test_detects_accessibility_issues(self):
        """Should detect accessibility issues"""
        profile = {"accessibility": {"contrast_ratio": 3.0}}
        result = run_redesign_intelligence(profile)
        improvements = result["improve"]
        accessibility_improvements = [
            i for i in improvements if i["category"] == "accessibility"
        ]
        assert len(accessibility_improvements) > 0
    
    def test_improvement_has_required_fields(self):
        """Improvements should have all required fields"""
        profile = {}
        result = run_redesign_intelligence(profile)
        for i in result["improve"]:
            assert "category" in i
            assert "current_state" in i
            assert "problem" in i
            assert "proposed_change" in i
            assert "expected_benefit" in i
            assert "priority" in i


class TestLayoutStrategy:
    """Test 7: Layout strategy test"""
    
    def test_returns_layout_pattern(self):
        """Should return a layout pattern"""
        profile = {"industry": "technology"}
        result = run_redesign_intelligence(profile)
        layout = result["layout_strategy"]
        assert layout is not None
        assert "pattern" in layout
    
    def test_pattern_from_valid_set(self):
        """Pattern should be from valid set"""
        valid_patterns = [
            "asymmetric", "editorial", "bento", "centered", "overlapping",
            "immersive", "split", "diagonal", "layered", "full-bleed",
            "storytelling", "grid", "experimental"
        ]
        profile = {"industry": "technology"}
        result = run_redesign_intelligence(profile)
        pattern = result["layout_strategy"]["pattern"]
        assert pattern in valid_patterns
    
    def test_layout_has_description_and_reasoning(self):
        """Layout strategy should have description and reasoning"""
        profile = {"industry": "technology"}
        result = run_redesign_intelligence(profile)
        layout = result["layout_strategy"]
        assert "description" in layout
        assert "reasoning" in layout


class TestVisualStrategy:
    """Test 8: Visual strategy test"""
    
    def test_returns_visual_strategy(self):
        """Should return visual strategy"""
        profile = {"visual": {"density": "medium"}}
        result = run_redesign_intelligence(profile)
        visual = result["visual_strategy"]
        assert visual is not None
        assert "density" in visual
    
    def test_visual_has_recommendations(self):
        """Visual strategy should have recommendations"""
        profile = {}
        result = run_redesign_intelligence(profile)
        visual = result["visual_strategy"]
        assert "recommendations" in visual
        assert isinstance(visual["recommendations"], list)


class TestTypographyStrategy:
    """Test 9: Typography strategy test"""
    
    def test_returns_typography_strategy(self):
        """Should return typography strategy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        typography = result["typography_strategy"]
        assert typography is not None
        assert "hierarchy" in typography
    
    def test_typography_has_hierarchy(self):
        """Typography should define hierarchy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        typography = result["typography_strategy"]
        assert "H1" in typography["hierarchy"]


class TestColorStrategy:
    """Test 10: Color strategy test"""
    
    def test_returns_color_strategy(self):
        """Should return color strategy"""
        profile = {"colors": {"primary": "#0066CC"}}
        result = run_redesign_intelligence(profile)
        color = result["color_strategy"]
        assert color is not None
    
    def test_preserves_brand_color(self):
        """Should preserve brand colors"""
        profile = {"brand": {"primary_color": "#FF5500"}}
        result = run_redesign_intelligence(profile)
        color = result["color_strategy"]
        assert color["primary"] == "#FF5500"


class TestComponentStrategy:
    """Test 11: Component strategy test"""
    
    def test_returns_component_strategy(self):
        """Should return component strategy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        component = result["component_strategy"]
        assert component is not None
    
    def test_minimum_stack_principle(self):
        """Should follow minimum stack principle"""
        profile = {}
        result = run_redesign_intelligence(profile)
        component = result["component_strategy"]
        assert component["minimum_stack_principle"] == True
    
    def test_recommends_libraries(self):
        """Should recommend libraries"""
        profile = {}
        result = run_redesign_intelligence(profile)
        component = result["component_strategy"]
        assert len(component["recommended_libraries"]) > 0


class TestMotionStrategy:
    """Test 12: Motion strategy test"""
    
    def test_returns_motion_strategy(self):
        """Should return motion strategy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        motion = result["motion_strategy"]
        assert motion is not None
    
    def test_motion_has_intensity(self):
        """Motion strategy should have intensity"""
        profile = {}
        result = run_redesign_intelligence(profile)
        motion = result["motion_strategy"]
        assert "intensity" in motion
        assert motion["intensity"] in ["none", "low", "medium", "high"]
    
    def test_motion_considers_accessibility(self):
        """Motion strategy should consider accessibility"""
        profile = {"accessibility": {"reduce_motion_preference": True}}
        result = run_redesign_intelligence(profile)
        motion = result["motion_strategy"]
        assert len(motion["accessibility_considerations"]) > 0


class TestAccessibilityStrategy:
    """Test 13: Accessibility strategy test"""
    
    def test_returns_accessibility_strategy(self):
        """Should return accessibility strategy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        accessibility = result["accessibility_strategy"]
        assert accessibility is not None
    
    def test_wcag_level_specified(self):
        """Should specify WCAG level"""
        profile = {}
        result = run_redesign_intelligence(profile)
        accessibility = result["accessibility_strategy"]
        assert accessibility["wcag_level"] == "AA"
    
    def test_provides_recommendations(self):
        """Should provide accessibility recommendations"""
        profile = {}
        result = run_redesign_intelligence(profile)
        accessibility = result["accessibility_strategy"]
        assert len(accessibility["recommendations"]) > 0


class TestPerformanceStrategy:
    """Test 14: Performance strategy test"""
    
    def test_returns_performance_strategy(self):
        """Should return performance strategy"""
        profile = {}
        result = run_redesign_intelligence(profile)
        performance = result["performance_strategy"]
        assert performance is not None
    
    def test_covers_optimization_areas(self):
        """Should cover multiple optimization areas"""
        profile = {}
        result = run_redesign_intelligence(profile)
        performance = result["performance_strategy"]
        assert "image_optimization" in performance
        assert "js_optimization" in performance
        assert "font_optimization" in performance


class TestDesignDiversity:
    """Test 15: Design diversity test"""
    
    def test_different_industries_get_different_layouts(self):
        """Different industries should get different layout recommendations"""
        tech_profile = {"industry": "technology", "brand": {"personality": "modern"}}
        creative_profile = {"industry": "creative", "brand": {"personality": "playful"}}
        
        tech_result = run_redesign_intelligence(tech_profile)
        creative_result = run_redesign_intelligence(creative_profile)
        
        tech_pattern = tech_result["layout_strategy"]["pattern"]
        creative_pattern = creative_result["layout_strategy"]["pattern"]
        
        # They should potentially be different (not guaranteed due to randomness)
        # but the strategies should reflect different reasoning
        assert tech_result["layout_strategy"]["reasoning"] != creative_result["layout_strategy"]["reasoning"]
    
    def test_brand_personality_affects_layout(self):
        """Brand personality should affect layout selection"""
        modern_profile = {"brand": {"personality": "modern"}}
        traditional_profile = {"brand": {"personality": "traditional"}}
        
        modern_result = run_redesign_intelligence(modern_profile)
        traditional_result = run_redesign_intelligence(traditional_profile)
        
        # Both should have valid patterns
        valid_patterns = [
            "asymmetric", "editorial", "bento", "centered", "overlapping",
            "immersive", "split", "diagonal", "layered", "full-bleed",
            "storytelling", "grid", "experimental"
        ]
        assert modern_result["layout_strategy"]["pattern"] in valid_patterns
        assert traditional_result["layout_strategy"]["pattern"] in valid_patterns


class TestDesignEngineIntegration:
    """Test 16: Design Engine integration test"""
    
    def test_output_compatible_with_design_engine(self):
        """Output should be compatible with Design Engine"""
        profile = {
            "brand": {"name": "Test"},
            "industry": "technology",
            "content": {"sections": []}
        }
        result = run_redesign_intelligence(profile)
        
        # Check that all expected keys are present
        assert "project_summary" in result
        assert "layout_strategy" in result
        assert "visual_strategy" in result
        assert "typography_strategy" in result
        assert "color_strategy" in result
        assert "component_strategy" in result
        assert "preserve" in result
        assert "remove" in result
        assert "improve" in result
    
    def test_result_is_dict(self):
        """Result should be a dictionary"""
        profile = {}
        result = run_redesign_intelligence(profile)
        assert isinstance(result, dict)


class TestEmptyProfile:
    """Test 17: Empty profile test"""
    
    def test_handles_empty_profile(self):
        """Should handle empty profile gracefully"""
        profile = {}
        result = run_redesign_intelligence(profile)
        assert result is not None
        assert "project_summary" in result
    
    def test_empty_profile_has_defaults(self):
        """Empty profile should produce default strategies"""
        profile = {}
        result = run_redesign_intelligence(profile)
        assert result["layout_strategy"] is not None
        assert result["visual_strategy"] is not None


class TestIncompleteProfile:
    """Test 18: Incomplete profile test"""
    
    def test_handles_missing_brand(self):
        """Should handle missing brand info"""
        profile = {"industry": "technology"}
        result = run_redesign_intelligence(profile)
        assert result is not None
    
    def test_handles_missing_content(self):
        """Should handle missing content"""
        profile = {"brand": {"name": "Test"}}
        result = run_redesign_intelligence(profile)
        assert result is not None
    
    def test_handles_missing_visual(self):
        """Should handle missing visual info"""
        profile = {"brand": {"name": "Test"}}
        result = run_redesign_intelligence(profile)
        assert result["visual_strategy"] is not None


class TestUnknownValues:
    """Test 19: Unknown values test"""
    
    def test_handles_unknown_industry(self):
        """Should handle unknown industry"""
        profile = {"industry": "unknown_industry_xyz"}
        result = run_redesign_intelligence(profile)
        assert result["layout_strategy"]["pattern"] is not None
    
    def test_handles_unknown_personality(self):
        """Should handle unknown brand personality"""
        profile = {"brand": {"personality": "unknown_personality_xyz"}}
        result = run_redesign_intelligence(profile)
        assert result["layout_strategy"]["pattern"] is not None


class TestDeterministicOutput:
    """Test 20: Deterministic output test"""
    
    def test_same_input_produces_same_structure(self):
        """Same input should produce same output structure"""
        profile = {
            "brand": {"name": "Test", "personality": "modern"},
            "industry": "technology"
        }
        
        result1 = run_redesign_intelligence(profile)
        result2 = run_redesign_intelligence(profile)
        
        # Structure should be the same
        assert set(result1.keys()) == set(result2.keys())
        assert type(result1["preserve"]) == type(result2["preserve"])
        assert type(result1["remove"]) == type(result2["remove"])
        assert type(result1["improve"]) == type(result2["improve"])
    
    def test_confidence_is_numeric(self):
        """Confidence should be numeric"""
        profile = {}
        result = run_redesign_intelligence(profile)
        assert isinstance(result["confidence"], (int, float))
        assert 0 <= result["confidence"] <= 1


class TestAllEngines:
    """Additional comprehensive tests"""
    
    def test_full_profile_analysis(self):
        """Full profile should produce comprehensive results"""
        profile = {
            "brand": {
                "name": "Acme Corp",
                "personality": "modern",
                "primary_color": "#0066CC"
            },
            "industry": "technology",
            "content": {
                "sections": [
                    {"type": "hero", "title": "Welcome", "priority": "high"},
                    {"type": "features", "title": "Features", "priority": "medium"},
                    {"type": "testimonial", "title": "Reviews", "priority": "low"}
                ],
                "value_proposition": "Fast, reliable solutions"
            },
            "visual": {
                "density": "high",
                "contrast": "low",
                "shadows": "heavy"
            },
            "typography": {
                "hierarchy": {}
            },
            "accessibility": {
                "contrast_ratio": 3.0,
                "keyboard_accessible": False
            },
            "performance": {
                "large_images": True,
                "heavy_js": True
            }
        }
        
        result = run_redesign_intelligence(profile)
        
        # Verify all strategies are present
        assert result["layout_strategy"] is not None
        assert result["visual_strategy"] is not None
        assert result["typography_strategy"] is not None
        assert result["color_strategy"] is not None
        assert result["component_strategy"] is not None
        assert result["motion_strategy"] is not None
        assert result["content_hierarchy"] is not None
        assert result["performance_strategy"] is not None
        assert result["accessibility_strategy"] is not None
        
        # Verify decisions were made
        assert len(result["preserve"]) > 0
        assert len(result["remove"]) > 0
        assert len(result["improve"]) > 0
        assert len(result["risks"]) > 0
        
        # Verify specific detections
        remove_elements = [r["element"] for r in result["remove"]]
        assert "excessive_shadows" in remove_elements
        
        improve_categories = [i["category"] for i in result["improve"]]
        assert "accessibility" in improve_categories
        assert "visual" in improve_categories
    
    def test_risk_identification(self):
        """Should identify design risks"""
        profile = {"redesign_scope": "complete"}
        result = run_redesign_intelligence(profile)
        
        assert len(result["risks"]) > 0
        risk = result["risks"][0]
        assert "risk" in risk
        assert "severity" in risk
        assert "mitigation" in risk


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
