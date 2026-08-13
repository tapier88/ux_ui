"""
Tests for Website Intelligence V0.1
"""
import sys
import os

# Add workspace to path
sys.path.insert(0, os.getcwd())


def _configure_stdout():
    """Make direct execution portable across Windows consoles."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


_configure_stdout()


def test_website_intelligence_imports():
    """Test that all required imports work"""
    from harness.skills.website_intelligence import (
        WebsiteDesignProfile,
        TechnologyStack,
        VisualDesign,
        Typography,
        Layout,
        ComponentLibrary,
        AccessibilityInfo,
        PerformanceMetrics,
        AIQualityScore,
        DesignStyle,
        ColorPalette,
        ColorInfo,
        WebsiteInspector,
        analyze_website,
        create_design_profile
    )
    print("[PASS] All imports successful")


def test_models_creation():
    """Test model creation"""
    from harness.skills.website_intelligence import (
        WebsiteDesignProfile, TechnologyStack, VisualDesign, Typography,
        Layout, ComponentLibrary, AccessibilityInfo, PerformanceMetrics,
        AIQualityScore, DesignStyle, ColorPalette, ColorInfo
    )
    
    # Create instances
    tech = TechnologyStack(frontend_frameworks=['React'])
    visual = VisualDesign(style=DesignStyle.MODERN)
    typography = Typography(font_families=['Inter'])
    layout = Layout(grid_type='flex', columns=12)
    components = ComponentLibrary(components=['Button'], component_count=1)
    accessibility = AccessibilityInfo(wcag_level='AA', compliance_score=0.85)
    performance = PerformanceMetrics(load_time=1.2, lighthouse_score=92)
    ai_quality = AIQualityScore(overall_score=0.88)
    
    profile = WebsiteDesignProfile(
        project_name='Test Project',
        technology_stack=tech,
        visual_design=visual,
        typography=typography,
        layout=layout,
        component_library=components,
        accessibility=accessibility,
        performance=performance,
        ai_quality=ai_quality
    )
    
    assert profile.project_name == 'Test Project'
    assert profile.technology_stack.frontend_frameworks == ['React']
    print("[PASS] Model creation successful")


def test_serialization_roundtrip():
    """Test serialization and deserialization"""
    from harness.skills.website_intelligence import (
        WebsiteDesignProfile, TechnologyStack, VisualDesign, DesignStyle
    )
    
    tech = TechnologyStack(frontend_frameworks=['React'], css_frameworks=['Tailwind CSS'])
    visual = VisualDesign(style=DesignStyle.MODERN)
    
    profile = WebsiteDesignProfile(
        project_name='Serialization Test',
        url='https://example.com',
        technology_stack=tech,
        visual_design=visual,
        patterns=['hero-section'],
        motion_effects=['transitions']
    )
    
    # Serialize
    data = profile.to_dict()
    assert data['project_name'] == 'Serialization Test'
    assert data['technology_stack']['frontend_frameworks'] == ['React']
    
    # Deserialize
    profile2 = WebsiteDesignProfile.from_dict(data)
    assert profile2.project_name == 'Serialization Test'
    assert profile2.url == 'https://example.com'
    assert profile2.technology_stack.frontend_frameworks == ['React']
    assert profile2.visual_design.style == DesignStyle.MODERN
    
    print("[PASS] Serialization roundtrip successful")


def _make_fixture_project(path):
    """
    Create a minimal but realistic project on disk for the inspector to
    read: a package.json declaring React + Tailwind, plus a components
    folder, so WebsiteInspector.inspect() has something real to detect
    instead of an empty directory.
    """
    import json
    import shutil

    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

    package_json = {
        "name": "test_website_project",
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        },
        "devDependencies": {
            "tailwindcss": "^3.4.0",
        },
    }
    with open(os.path.join(path, "package.json"), "w") as f:
        json.dump(package_json, f)

    components_dir = os.path.join(path, "components")
    os.makedirs(components_dir)
    with open(os.path.join(components_dir, "Header.tsx"), "w") as f:
        f.write("export default function Header() { return null; }\n")
    with open(os.path.join(components_dir, "Footer.tsx"), "w") as f:
        f.write("export default function Footer() { return null; }\n")


def test_inspector_with_project():
    """Test WebsiteInspector with a real project"""
    import shutil
    from harness.skills.website_intelligence import WebsiteInspector

    fixture_path = '/tmp/test_website_project'
    _make_fixture_project(fixture_path)
    try:
        inspector = WebsiteInspector(project_path=fixture_path)
        profile = inspector.inspect(url='https://example.com')

        assert profile.project_name == 'test_website_project'
        assert profile.url == 'https://example.com'

        assert profile.technology_stack is not None
        assert 'React' in profile.technology_stack.frontend_frameworks
        assert 'Tailwind CSS' in profile.technology_stack.css_frameworks

        assert profile.component_library is not None
        assert profile.component_library.component_count > 0

        print("[PASS] Inspector with project successful")
    finally:
        shutil.rmtree(fixture_path, ignore_errors=True)


def test_inspector_empty_project():
    """Test WebsiteInspector with non-existent project"""
    from harness.skills.website_intelligence import WebsiteInspector
    
    inspector = WebsiteInspector(project_path='/nonexistent/path')
    profile = inspector.inspect()
    
    assert profile.project_name == 'unknown'
    assert profile.url is None
    
    print("[PASS] Inspector empty project handling successful")


def test_skill_registry_integration():
    """Test website-intelligence skill registration"""
    from harness.skills import get_skill_registry
    from harness.skills.website_intelligence import register_website_intelligence_skill
    
    registry = get_skill_registry()
    register_website_intelligence_skill(registry)
    
    assert registry.has_skill('website-intelligence')
    assert registry.is_skill_loaded('website-intelligence')
    
    # Execute skill
    result = registry.execute_skill('website-intelligence', project_path='/tmp/test_website_project')
    assert isinstance(result, dict)
    assert 'project_name' in result
    
    print("[PASS] Skill registry integration successful")


def test_design_style_enum():
    """Test DesignStyle enum values"""
    from harness.skills.website_intelligence import DesignStyle
    
    assert DesignStyle.MINIMALIST.value == 'minimalist'
    assert DesignStyle.MODERN.value == 'modern'
    assert DesignStyle.UNKNOWN.value == 'unknown'
    
    print("[PASS] DesignStyle enum successful")


def test_color_palette():
    """Test ColorPalette functionality"""
    from harness.skills.website_intelligence import ColorPalette, ColorInfo, ColorPaletteType
    
    colors = [
        ColorInfo(hex='#3b82f6', rgb=(59, 130, 246), usage='primary'),
        ColorInfo(hex='#1d4ed8', rgb=(29, 78, 216), usage='secondary')
    ]
    
    palette = ColorPalette(colors=colors, palette_type=ColorPaletteType.COMPLEMENTARY)
    
    data = palette.to_dict()
    assert len(data['colors']) == 2
    assert data['palette_type'] == 'complementary'
    
    palette2 = ColorPalette.from_dict(data)
    assert len(palette2.colors) == 2
    assert palette2.colors[0].hex == '#3b82f6'
    
    print("[PASS] ColorPalette functionality successful")


def run_all_website_tests():
    """Run all Website Intelligence tests"""
    tests = [
        ('Imports', test_website_intelligence_imports),
        ('Models', test_models_creation),
        ('Serialization', test_serialization_roundtrip),
        ('Inspector (project)', test_inspector_with_project),
        ('Inspector (empty)', test_inspector_empty_project),
        ('Skill Registry', test_skill_registry_integration),
        ('DesignStyle Enum', test_design_style_enum),
        ('ColorPalette', test_color_palette),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 50)
    print("WEBSITE INTELLIGENCE V0.1 - TEST SUITE")
    print("=" * 50 + "\n")
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Website Intelligence Tests: {passed}/{len(tests)} passed")
    print("=" * 50)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_website_tests()
    sys.exit(0 if success else 1)
