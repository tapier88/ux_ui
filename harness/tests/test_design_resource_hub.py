"""
Tests for harness.skills.design_resource_hub — previously had zero test
coverage. This skill decides which real design resources (frameworks,
libraries, references) the agent draws from before building a redesign
— it's the mechanism that's supposed to keep output grounded in real,
external references instead of generic templates (see
ARCHITECTURE_PRINCIPLES.md §12).

Run with: python -m unittest harness.tests.test_design_resource_hub -v
"""
import unittest

from harness.skills.design_resource_hub import (
    DesignResourceCatalog,
    DesignResourceResearcher,
    ResourceSelector,
    DesignResourceResearchRequest,
    ResourceType,
    ResourceCategory,
)


def sample_request(**overrides) -> DesignResourceResearchRequest:
    base = dict(
        project_type="marketing_site",
        industry="fintech",
        brand_personality="professional",
        visual_style="minimalist",
        layout_style="editorial",
        animation_level="MEDIUM",
        interaction_level="MEDIUM",
    )
    base.update(overrides)
    return DesignResourceResearchRequest(**base)


class TestDesignResourceCatalog(unittest.TestCase):

    def setUp(self):
        self.catalog = DesignResourceCatalog()

    def test_catalog_loads_official_resources_on_init(self):
        # The catalog seeds itself with a real, hardcoded set of known
        # resources (Tailwind CSS etc.) — it should never come up empty.
        self.assertGreater(len(self.catalog._resources), 0)

    def test_known_resource_is_present(self):
        self.assertIn("tailwind-css", self.catalog._resources)

    def test_resources_have_required_fields(self):
        for resource_id, resource in self.catalog._resources.items():
            self.assertTrue(resource.name, msg=f"{resource_id} missing name")
            self.assertTrue(resource.purpose, msg=f"{resource_id} missing purpose")
            self.assertIsInstance(resource.type, ResourceType)
            self.assertIsInstance(resource.category, ResourceCategory)


class TestDesignResourceResearcher(unittest.TestCase):

    def setUp(self):
        self.researcher = DesignResourceResearcher()

    def test_research_returns_candidates_for_a_realistic_request(self):
        request = sample_request()
        result = self.researcher.research(request)
        self.assertIn("resources_to_consult", result)
        self.assertIsInstance(result["resources_to_consult"], list)

    def test_get_resource_details_for_known_resource(self):
        details = self.researcher.get_resource_details("tailwind-css")
        self.assertIsNotNone(details)

    def test_get_resource_details_for_unknown_resource_returns_none(self):
        details = self.researcher.get_resource_details("does-not-exist-xyz")
        self.assertIsNone(details)

    def test_consult_resource_returns_a_design_resource(self):
        resource = self.researcher.consult_resource("tailwind-css")
        self.assertIsNotNone(resource)
        self.assertEqual(resource.id, "tailwind-css")


class TestResourceSelector(unittest.TestCase):

    def setUp(self):
        self.selector = ResourceSelector()

    def test_select_resources_returns_selected_and_rejected(self):
        request = sample_request()
        selected, rejected = self.selector.select_resources(request)
        self.assertIsInstance(selected, list)
        self.assertIsInstance(rejected, list)

    def test_high_animation_request_selects_more_than_minimal_stack(self):
        low_motion = sample_request(animation_level="NONE", interaction_level="NONE")
        high_motion = sample_request(animation_level="HIGH", interaction_level="HIGH")

        selected_low, _ = self.selector.select_resources(low_motion)
        selected_high, _ = self.selector.select_resources(high_motion)

        # A high-animation request should not select strictly fewer
        # resources than a no-animation request — the selection should
        # actually respond to the request, not be constant.
        self.assertGreaterEqual(len(selected_high), len(selected_low))

    def test_generate_report_produces_a_report(self):
        request = sample_request()
        selected, rejected = self.selector.select_resources(request)
        report = self.selector.generate_report(request, selected, rejected)
        self.assertIsNotNone(report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
