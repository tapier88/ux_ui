"""
Tests for Redesign Intelligence Skill V0.1
"""
import unittest
from typing import Dict, Any


class TestRedesignIntelligenceImport(unittest.TestCase):
    """Test 1: Import tests"""
    
    def test_import_models(self):
        """Test that models can be imported"""
        from harness.skills.redesign_intelligence.models import (
            RedesignStrategy,
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
        )
        
    def test_import_engine(self):
        """Test that engine can be imported"""
        from harness.skills.redesign_intelligence.engine import (
            RedesignIntelligenceEngine,
            PreserveEngine,
            RemoveEngine,
            ImprovementEngine,
        )
        
    def test_import_skill(self):
        """Test that skill function can be imported"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill


class TestRedesignIntelligenceModels(unittest.TestCase):
    """Test 2: Model tests"""
    
    def test_preserve_decision_to_dict(self):
        """Test PreserveDecision serialization"""
        from harness.skills.redesign_intelligence.models import PreserveDecision
        
        decision = PreserveDecision(
            element="logo",
            reason="Brand identifier",
            confidence=0.95
        )
        
        result = decision.to_dict()
        self.assertEqual(result["element"], "logo")
        self.assertEqual(result["reason"], "Brand identifier")
        self.assertEqual(result["confidence"], 0.95)
    
    def test_remove_decision_to_dict(self):
        """Test RemoveDecision serialization"""
        from harness.skills.redesign_intelligence.models import RemoveDecision
        
        decision = RemoveDecision(
            element="excessive shadows",
            reason="Reduces clarity",
            confidence=0.8
        )
        
        result = decision.to_dict()
        self.assertEqual(result["element"], "excessive shadows")
        self.assertEqual(result["reason"], "Reduces clarity")
    
    def test_improve_decision_to_dict(self):
        """Test ImproveDecision serialization"""
        from harness.skills.redesign_intelligence.models import (
            ImproveDecision,
            ImprovementCategory,
            Priority,
        )
        
        decision = ImproveDecision(
            category=ImprovementCategory.VISUAL,
            current_state="High density",
            problem="Too many elements",
            proposed_change="Increase whitespace",
            expected_benefit="Better readability",
            priority=Priority.HIGH,
            confidence=0.85
        )
        
        result = decision.to_dict()
        self.assertEqual(result["category"], "visual")
        self.assertEqual(result["priority"], "high")
    
    def test_layout_strategy_to_dict(self):
        """Test LayoutStrategy serialization"""
        from harness.skills.redesign_intelligence.models import (
            LayoutStrategy,
            LayoutPattern,
        )
        
        strategy = LayoutStrategy(
            recommended_pattern=LayoutPattern.ASYMMETRIC,
            reasoning="Test reasoning"
        )
        
        result = strategy.to_dict()
        self.assertEqual(result["recommended_pattern"], "asymmetric")
    
    def test_redesign_strategy_to_dict(self):
        """Test RedesignStrategy serialization"""
        from harness.skills.redesign_intelligence.models import RedesignStrategy
        
        strategy = RedesignStrategy(
            project_summary="Test summary",
            confidence=0.8
        )
        
        result = strategy.to_dict()
        self.assertEqual(result["project_summary"], "Test summary")
        self.assertEqual(result["confidence"], 0.8)


class TestSkillRegistry(unittest.TestCase):
    """Test 3: Skill registry tests"""
    
    def test_skill_registered(self):
        """Test that redesign-intelligence skill is registered"""
        from harness.skills import get_skill_registry
        
        registry = get_skill_registry()
        self.assertTrue(registry.has_skill("redesign-intelligence"))
    
    def test_skill_loaded(self):
        """Test that redesign-intelligence skill is loaded"""
        from harness.skills import get_skill_registry
        
        registry = get_skill_registry()
        self.assertTrue(registry.is_skill_loaded("redesign-intelligence"))
    
    def test_skill_execution(self):
        """Test skill execution via registry"""
        from harness.skills import get_skill_registry
        
        registry = get_skill_registry()
        profile = {"industry": "tech"}
        result = registry.execute_skill("redesign-intelligence", profile=profile)
        
        self.assertIsInstance(result, dict)
        self.assertIn("project_summary", result)


class TestPreserveEngine(unittest.TestCase):
    """Test 4: Preserve engine tests"""
    
    def test_preserve_brand_elements(self):
        """Test preservation of brand elements"""
        from harness.skills.redesign_intelligence.engine import PreserveEngine
        
        engine = PreserveEngine()
        profile = {
            "brand": {
                "logo": True,
                "colors": {"primary": "#FF5722"},
                "value_proposition": "Test value"
            }
        }
        
        decisions = engine.analyze(profile)
        self.assertGreater(len(decisions), 0)
        
        elements = [d.element for d in decisions]
        self.assertIn("logo", elements)
    
    def test_preserve_empty_profile(self):
        """Test preserve engine with empty profile"""
        from harness.skills.redesign_intelligence.engine import PreserveEngine
        
        engine = PreserveEngine()
        decisions = engine.analyze({})
        self.assertEqual(len(decisions), 0)


class TestRemoveEngine(unittest.TestCase):
    """Test 5: Remove engine tests"""
    
    def test_remove_decorative_elements(self):
        """Test removal of decorative elements"""
        from harness.skills.redesign_intelligence.engine import RemoveEngine
        
        engine = RemoveEngine()
        profile = {
            "visual": {
                "excessive_shadows": True,
                "arbitrary_gradients": True
            }
        }
        
        decisions = engine.analyze(profile)
        self.assertGreater(len(decisions), 0)
        
        elements = [d.element for d in decisions]
        self.assertIn("excessive shadows", elements)
    
    def test_remove_empty_profile(self):
        """Test remove engine with empty profile"""
        from harness.skills.redesign_intelligence.engine import RemoveEngine
        
        engine = RemoveEngine()
        decisions = engine.analyze({})
        self.assertEqual(len(decisions), 0)


class TestImprovementEngine(unittest.TestCase):
    """Test 6: Improvement engine tests"""
    
    def test_visual_improvements(self):
        """Test visual improvement detection"""
        from harness.skills.redesign_intelligence.engine import ImprovementEngine
        
        engine = ImprovementEngine()
        profile = {
            "visual": {
                "density": "high",
                "contrast": "low"
            }
        }
        
        improvements = engine.analyze(profile)
        self.assertGreater(len(improvements), 0)
    
    def test_accessibility_improvements(self):
        """Test accessibility improvement detection"""
        from harness.skills.redesign_intelligence.engine import ImprovementEngine
        from harness.skills.redesign_intelligence.models import ImprovementCategory
        
        engine = ImprovementEngine()
        profile = {
            "accessibility": {
                "issues": True
            }
        }
        
        improvements = engine.analyze(profile)
        accessibility_improvements = [
            i for i in improvements 
            if i.category == ImprovementCategory.ACCESSIBILITY
        ]
        self.assertGreater(len(accessibility_improvements), 0)


class TestLayoutStrategy(unittest.TestCase):
    """Test 7: Layout strategy tests"""
    
    def test_creative_industry_layout(self):
        """Test layout for creative industry"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        profile = {"industry": "creative"}
        
        strategy = engine.analyze(profile)
        # Creative industries should get experimental or asymmetric layouts
        self.assertIn(
            strategy.recommended_pattern.value,
            ["experimental", "asymmetric", "immersive"]
        )
    
    def test_corporate_industry_layout(self):
        """Test layout for corporate industry"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        profile = {"industry": "corporate"}
        
        strategy = engine.analyze(profile)
        # Corporate should get grid or centered layouts
        self.assertIn(
            strategy.recommended_pattern.value,
            ["grid", "centered"]
        )
    
    def test_bold_personality_layout(self):
        """Test layout for bold brand personality"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        profile = {
            "brand": {"personality": "bold"}
        }
        
        strategy = engine.analyze(profile)
        # Bold personality should get diagonal or asymmetric
        self.assertIn(
            strategy.recommended_pattern.value,
            ["diagonal", "asymmetric"]
        )


class TestVisualStrategy(unittest.TestCase):
    """Test 8: Visual strategy tests"""
    
    def test_high_density_recommendations(self):
        """Test visual recommendations for high density"""
        from harness.skills.redesign_intelligence.engine import VisualStrategyEngine
        
        engine = VisualStrategyEngine()
        profile = {
            "visual": {"density": "high"}
        }
        
        strategy = engine.analyze(profile)
        self.assertGreater(len(strategy.recommendations), 0)
    
    def test_low_contrast_recommendations(self):
        """Test visual recommendations for low contrast"""
        from harness.skills.redesign_intelligence.engine import VisualStrategyEngine
        
        engine = VisualStrategyEngine()
        profile = {
            "visual": {"contrast": "low"}
        }
        
        strategy = engine.analyze(profile)
        recommendations_str = " ".join(strategy.recommendations).lower()
        self.assertIn("contrast", recommendations_str)


class TestTypographyStrategy(unittest.TestCase):
    """Test 9: Typography strategy tests"""
    
    def test_hierarchy_defined(self):
        """Test that typography hierarchy is defined"""
        from harness.skills.redesign_intelligence.engine import TypographyStrategyEngine
        
        engine = TypographyStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertIn("H1", strategy.hierarchy)
        self.assertIn("H2", strategy.hierarchy)
        self.assertIn("body", strategy.hierarchy)
    
    def test_font_sizes_defined(self):
        """Test that font sizes are defined"""
        from harness.skills.redesign_intelligence.engine import TypographyStrategyEngine
        
        engine = TypographyStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertIn("H1", strategy.font_sizes)
        self.assertIn("body", strategy.font_sizes)


class TestColorStrategy(unittest.TestCase):
    """Test 10: Color strategy tests"""
    
    def test_brand_preservation(self):
        """Test brand color preservation"""
        from harness.skills.redesign_intelligence.engine import ColorStrategyEngine
        
        engine = ColorStrategyEngine()
        profile = {
            "brand": {"preserve_colors": True},
            "colors": {"primary": "#FF5722"}
        }
        
        strategy = engine.analyze(profile)
        self.assertTrue(strategy.brand_preservation)
        self.assertEqual(strategy.primary, "#FF5722")
    
    def test_default_colors(self):
        """Test default color values"""
        from harness.skills.redesign_intelligence.engine import ColorStrategyEngine
        
        engine = ColorStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertEqual(strategy.background, "#FFFFFF")
        self.assertEqual(strategy.foreground, "#1A1A1A")


class TestComponentStrategy(unittest.TestCase):
    """Test 11: Component strategy tests"""
    
    def test_minimum_stack_principle(self):
        """Test minimum stack principle is enforced"""
        from harness.skills.redesign_intelligence.engine import ComponentStrategyEngine
        
        engine = ComponentStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertTrue(strategy.minimum_stack_principle)
    
    def test_essential_components_created(self):
        """Test that essential components are marked for creation"""
        from harness.skills.redesign_intelligence.engine import ComponentStrategyEngine
        from harness.skills.redesign_intelligence.models import ComponentAction
        
        engine = ComponentStrategyEngine()
        strategy = engine.analyze({})
        
        # Check for essential components
        component_names = [c.component_name for c in strategy.components]
        self.assertIn("Navigation", component_names)
        self.assertIn("Hero", component_names)


class TestMotionStrategy(unittest.TestCase):
    """Test 12: Motion strategy tests"""
    
    def test_accessibility_considerations(self):
        """Test motion accessibility considerations"""
        from harness.skills.redesign_intelligence.engine import MotionStrategyEngine
        
        engine = MotionStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertIn("Respect prefers-reduced-motion", strategy.accessibility_considerations)
    
    def test_performance_priority(self):
        """Test performance priority is set"""
        from harness.skills.redesign_intelligence.engine import MotionStrategyEngine
        
        engine = MotionStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertTrue(strategy.performance_priority)


class TestAccessibilityStrategy(unittest.TestCase):
    """Test 13: Accessibility strategy tests"""
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation recommendations"""
        from harness.skills.redesign_intelligence.engine import AccessibilityStrategyEngine
        
        engine = AccessibilityStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertGreater(len(strategy.keyboard_navigation), 0)
    
    def test_wcag_compliance(self):
        """Test WCAG compliance recommendation"""
        from harness.skills.redesign_intelligence.engine import AccessibilityStrategyEngine
        
        engine = AccessibilityStrategyEngine()
        strategy = engine.analyze({})
        
        recommendations_str = " ".join(strategy.recommendations).lower()
        self.assertIn("wcag", recommendations_str)


class TestPerformanceStrategy(unittest.TestCase):
    """Test 14: Performance strategy tests"""
    
    def test_image_optimization(self):
        """Test image optimization recommendations"""
        from harness.skills.redesign_intelligence.engine import PerformanceStrategyEngine
        
        engine = PerformanceStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertGreater(len(strategy.image_optimization), 0)
    
    def test_lazy_loading(self):
        """Test lazy loading recommendations"""
        from harness.skills.redesign_intelligence.engine import PerformanceStrategyEngine
        
        engine = PerformanceStrategyEngine()
        strategy = engine.analyze({})
        
        self.assertGreater(len(strategy.lazy_loading), 0)


class TestDesignDiversity(unittest.TestCase):
    """Test 15: Design diversity tests"""
    
    def test_different_industries_different_layouts(self):
        """Test that different industries get different layouts"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        
        creative = engine.analyze({"industry": "creative"})
        corporate = engine.analyze({"industry": "corporate"})
        fashion = engine.analyze({"industry": "fashion"})
        
        # At least some should be different
        patterns = [
            creative.recommended_pattern.value,
            corporate.recommended_pattern.value,
            fashion.recommended_pattern.value
        ]
        
        # Not all should be the same
        self.assertNotEqual(len(set(patterns)), 1)
    
    def test_different_personalities_different_layouts(self):
        """Test that different personalities get different layouts"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        
        bold = engine.analyze({"brand": {"personality": "bold"}})
        elegant = engine.analyze({"brand": {"personality": "elegant"}})
        playful = engine.analyze({"brand": {"personality": "playful"}})
        
        patterns = [
            bold.recommended_pattern.value,
            elegant.recommended_pattern.value,
            playful.recommended_pattern.value
        ]
        
        # Not all should be the same
        self.assertNotEqual(len(set(patterns)), 1)


class TestDesignEngineIntegration(unittest.TestCase):
    """Test 16: Design Engine integration tests"""
    
    def test_output_compatible_with_dict(self):
        """Test that output is dictionary-compatible for Design Engine"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill
        
        profile = {"industry": "tech"}
        result = redesign_intelligence_skill(profile)
        
        self.assertIsInstance(result, dict)
        self.assertIn("project_summary", result)
        self.assertIn("preserve", result)
        self.assertIn("remove", result)
        self.assertIn("improve", result)


class TestEmptyProfile(unittest.TestCase):
    """Test 17: Empty profile tests"""
    
    def test_empty_profile_handling(self):
        """Test handling of empty profile"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill
        
        result = redesign_intelligence_skill({})
        
        self.assertIsInstance(result, dict)
        self.assertIn("project_summary", result)
        self.assertIn("No profile data", result["project_summary"])
    
    def test_empty_profile_low_confidence(self):
        """Test that empty profile results in low confidence"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill
        
        result = redesign_intelligence_skill({})
        
        self.assertLess(result["confidence"], 0.5)


class TestIncompleteProfile(unittest.TestCase):
    """Test 18: Incomplete profile tests"""
    
    def test_partial_profile_handling(self):
        """Test handling of partial profile"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill
        
        profile = {"industry": "tech"}  # Only industry provided
        result = redesign_intelligence_skill(profile)
        
        self.assertIsInstance(result, dict)
        self.assertIn("project_summary", result)
        self.assertIn("tech", result["project_summary"])
    
    def test_missing_optional_fields(self):
        """Test handling when optional fields are missing"""
        from harness.skills.redesign_intelligence.engine import RedesignIntelligenceEngine
        
        engine = RedesignIntelligenceEngine()
        profile = {
            "industry": "ecommerce",
            "goals": ["conversion"]
            # Missing brand, visual, etc.
        }
        
        strategy = engine.analyze(profile)
        self.assertIsNotNone(strategy)


class TestUnknownValues(unittest.TestCase):
    """Test 19: Unknown values tests"""
    
    def test_unknown_industry(self):
        """Test handling of unknown industry"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        profile = {"industry": "unknown_industry_xyz"}
        
        strategy = engine.analyze(profile)
        # Should still return a valid strategy
        self.assertIsNotNone(strategy.recommended_pattern)
    
    def test_unknown_personality(self):
        """Test handling of unknown brand personality"""
        from harness.skills.redesign_intelligence.engine import MotionStrategyEngine
        
        engine = MotionStrategyEngine()
        profile = {"brand": {"personality": "unknown_personality"}}
        
        strategy = engine.analyze(profile)
        # Should default to subtle
        self.assertEqual(strategy.intensity, "subtle")


class TestDeterministicOutput(unittest.TestCase):
    """Test 20: Deterministic output tests"""
    
    def test_same_input_same_output(self):
        """Test that same input produces same output"""
        from harness.skills.redesign_intelligence import redesign_intelligence_skill
        
        profile = {
            "industry": "tech",
            "brand": {"personality": "bold"},
            "goals": ["conversion"]
        }
        
        result1 = redesign_intelligence_skill(profile)
        result2 = redesign_intelligence_skill(profile)
        
        # Key fields should be identical
        self.assertEqual(
            result1["layout_strategy"]["recommended_pattern"],
            result2["layout_strategy"]["recommended_pattern"]
        )
        self.assertEqual(
            result1["project_summary"],
            result2["project_summary"]
        )
    
    def test_layout_determinism(self):
        """Test layout strategy determinism"""
        from harness.skills.redesign_intelligence.engine import LayoutStrategyEngine
        
        engine = LayoutStrategyEngine()
        profile = {"industry": "creative", "brand": {"personality": "bold"}}
        
        strategy1 = engine.analyze(profile)
        strategy2 = engine.analyze(profile)
        
        self.assertEqual(
            strategy1.recommended_pattern,
            strategy2.recommended_pattern
        )


def run_tests():
    """Run all redesign intelligence tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestRedesignIntelligenceImport,
        TestRedesignIntelligenceModels,
        TestSkillRegistry,
        TestPreserveEngine,
        TestRemoveEngine,
        TestImprovementEngine,
        TestLayoutStrategy,
        TestVisualStrategy,
        TestTypographyStrategy,
        TestColorStrategy,
        TestComponentStrategy,
        TestMotionStrategy,
        TestAccessibilityStrategy,
        TestPerformanceStrategy,
        TestDesignDiversity,
        TestDesignEngineIntegration,
        TestEmptyProfile,
        TestIncompleteProfile,
        TestUnknownValues,
        TestDeterministicOutput,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
