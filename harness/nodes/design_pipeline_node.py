"""
DesignPipelineNode - Wires the full 5-stage design pipeline into the
graph execution engine.

This is the node the harness never had: harness/skills/ contains five
real, individually-tested skills (website_intelligence,
redesign_intelligence, design_resource_hub, design_execution_planner,
site_builder), matching exactly the pipeline documented in
site_builder/SKILL.md:

    WEBSITE
      -> WEBSITE INTELLIGENCE
      -> REDESIGN INTELLIGENCE
      -> DESIGN RESOURCE HUB
      -> DESIGN EXECUTION PLANNER
      -> SITE BUILDER
      -> CODE MODIFICATION

but nothing ever called them in sequence - each was only exercised in
isolation by its own test suite. This node runs all five stages against
a real project path and returns the build report, so the harness can
actually produce output instead of just passing unit tests.

Usage inside a graph:

    from harness.nodes.design_pipeline_node import DesignPipelineNode

    node = DesignPipelineNode(project_path="/path/to/site")
    result = node.execute(state)
    if result["status"] == "completed":
        print(result["report"])
"""
from typing import Any, Optional

from harness.core.graph import NodeType
from harness.core.state import TaskState
from harness.nodes import BaseNode


class DesignPipelineNode(BaseNode):
    """
    Runs the full website_intelligence -> redesign_intelligence ->
    design_resource_hub -> design_execution_planner -> site_builder
    sequence against a real project on disk.

    Expects on state.inputs (all optional, sensible defaults applied):
        project_path (str): path to the project to inspect and modify.
            Defaults to the value passed to the constructor.
        url (str): URL of the live site, if any (informational, passed
            to the inspector).
        resource_hub_options (dict): overrides for the Design Resource
            Hub request (project_type, industry, brand_personality,
            etc.) - see design_resource_hub.registry for the full list.
        dry_run (bool): if True, stops before site_builder actually
            writes files, and returns the build plan instead of a
            build report. Useful for reviewing what would change
            before committing to it. Defaults to True - callers must
            opt in to actually writing files.
    """

    def __init__(
        self,
        node_id: str = "DESIGN_PIPELINE_NODE",
        name: str = "Design Pipeline Node",
        project_path: str = ".",
    ):
        super().__init__(node_id, name, NodeType.STANDARD)
        self.project_path = project_path

    def execute(self, state: TaskState) -> dict:
        project_path = state.inputs.get("project_path", self.project_path)
        url = state.inputs.get("url")
        resource_hub_options = state.inputs.get("resource_hub_options", {})
        dry_run = state.inputs.get("dry_run", True)
        governance_threshold = state.inputs.get("governance_threshold", 75.0)
        governance_record_to_memory = state.inputs.get("governance_record_to_memory", False)

        stages: dict = {}

        # 1. Website Intelligence - inspect what's there now
        try:
            from harness.skills.website_intelligence import WebsiteInspector

            inspector = WebsiteInspector(project_path=project_path)
            profile = inspector.inspect(url=url)
            profile_dict = profile.to_dict()
            stages["website_intelligence"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "website_intelligence", e, stages)

        # 2. Redesign Intelligence - decide what to preserve/remove/improve
        try:
            from harness.skills.redesign_intelligence import redesign_intelligence_skill

            redesign_result = redesign_intelligence_skill(profile_dict)
            stages["redesign_intelligence"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "redesign_intelligence", e, stages)

        # 3. Design Resource Hub - select the resources/stack to use
        try:
            from harness.skills.design_resource_hub.registry import (
                design_resource_hub_execute,
            )

            resource_result = design_resource_hub_execute(resource_hub_options)
            stages["design_resource_hub"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "design_resource_hub", e, stages)

        # 4. Design Execution Planner - turn strategy into a concrete build plan
        try:
            from harness.skills.design_execution_planner import DesignExecutionPlanner

            planner = DesignExecutionPlanner()
            build_plan = planner.create_build_plan(
                project_name=profile_dict.get("project_name", "project"),
                design_profile=profile_dict,
                redesign_strategy=redesign_result,
                resource_report=resource_result.get("report"),
                existing_code=None,
            )
            stages["design_execution_planner"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "design_execution_planner", e, stages)

        # 5. Governance Gate - deterministic quality gate before any disk write.
        try:
            from harness.core.governance import GovernanceGate

            plan_dict = build_plan.to_dict()
            signals = state.inputs.get("governance_signals") or self._build_governance_signals(
                profile_dict=profile_dict,
                redesign_result=redesign_result,
                plan_dict=plan_dict,
            )
            gate = GovernanceGate(
                threshold=governance_threshold,
                record_to_memory=governance_record_to_memory,
            )
            governance_result = gate.evaluate(
                signals=signals,
                task_id=state.task_id,
                subject=profile_dict.get("url")
                or profile_dict.get("project_name")
                or project_path,
            )
            stages["governance_gate"] = {
                "status": "completed" if governance_result.passed else "blocked",
                "result": governance_result.to_dict(),
            }
        except Exception as e:
            return self._failure(state.task_id, "governance_gate", e, stages)

        if dry_run:
            return {
                "node": "DesignPipelineNode",
                "task_id": state.task_id,
                "status": "dry_run_completed",
                "stages": stages,
                "build_plan": plan_dict,
                "governance": governance_result.to_dict(),
            }

        if not governance_result.passed:
            return {
                "node": "DesignPipelineNode",
                "task_id": state.task_id,
                "status": "blocked",
                "failed_stage": "governance_gate",
                "stages": stages,
                "governance": governance_result.to_dict(),
            }

        # 6. Site Builder - actually write the code changes
        try:
            from harness.skills.site_builder import SiteBuilder

            # site_builder.execute_build() expects a plain dict (its own
            # _handle_* methods call design_build_plan.get(...) throughout),
            # not the DesignBuildPlan object design_execution_planner
            # returns. Also bridge the naming mismatch between the two
            # skills: design_execution_planner emits "typography_plan",
            # "layout_plan", "performance_plan", "accessibility_plan",
            # while site_builder reads "typography", "layout",
            # "performance", "accessibility" (no suffix). Today most of
            # those _handle_* methods are unimplemented stubs on the
            # site_builder side (see PLAN.md), so this bridge doesn't
            # change behavior yet - but it's the correct contract so the
            # data is there once those methods are actually implemented.
            plan_dict = self._adapt_build_plan_for_site_builder(plan_dict)

            builder = SiteBuilder(project_path)
            report = builder.execute_build(plan_dict)
            stages["site_builder"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "site_builder", e, stages)

        return {
            "node": "DesignPipelineNode",
            "task_id": state.task_id,
            "status": "completed",
            "stages": stages,
            "governance": governance_result.to_dict(),
            "report": report.to_dict(),
        }

    @staticmethod
    def _build_governance_signals(
        profile_dict: dict,
        redesign_result: dict,
        plan_dict: dict,
    ) -> list:
        """Build auditable governance signals from concrete pipeline outputs."""
        from harness.core.governance import ElevationSignal

        tokens = plan_dict.get("design_tokens", {})
        colors = tokens.get("colors", {}) if isinstance(tokens, dict) else {}
        typography = tokens.get("typography", {}) if isinstance(tokens, dict) else {}
        sections = plan_dict.get("sections", [])
        components = plan_dict.get("components", [])
        pages = plan_dict.get("pages", [])
        accessibility = plan_dict.get("accessibility_plan", {})
        performance = plan_dict.get("performance_plan", {})
        interactions = plan_dict.get("interactions", [])
        resource_usage = plan_dict.get("resource_usage", [])

        preserve_decisions = redesign_result.get("preserve", []) if isinstance(redesign_result, dict) else []
        brand_inputs = profile_dict.get("branding", {}) if isinstance(profile_dict, dict) else {}
        brand_score_parts = [
            bool(colors.get("primary")),
            bool(colors.get("text")),
            bool(colors.get("background")),
            bool(typography.get("font_family")),
            bool(preserve_decisions) or bool(brand_inputs),
        ]
        brand_score = DesignPipelineNode._score_ratio(brand_score_parts)

        accessibility_score_parts = [
            accessibility.get("semantic_html") is True,
            accessibility.get("keyboard_navigation") is True,
            accessibility.get("reduced_motion") is True,
            isinstance(accessibility.get("focus_states"), dict) and bool(accessibility.get("focus_states")),
            isinstance(accessibility.get("touch_targets"), dict) and bool(accessibility.get("touch_targets")),
            isinstance(accessibility.get("contrast"), dict)
            and float(accessibility.get("contrast", {}).get("min_ratio", 0)) >= 4.5,
        ]
        accessibility_score = DesignPipelineNode._score_ratio(accessibility_score_parts)

        expected_sections = max(
            (len(page.get("sections", [])) for page in pages if isinstance(page, dict)),
            default=0,
        )
        section_layouts = {
            section.get("layout")
            for section in sections
            if isinstance(section, dict) and section.get("layout")
        }
        visual_score_parts = [
            len(sections) >= expected_sections and expected_sections > 0,
            len(components) >= 3,
            len(section_layouts) >= 3,
            bool(colors),
            bool(typography),
        ]
        visual_score = DesignPipelineNode._score_ratio(visual_score_parts)

        image_optimization = performance.get("image_optimization", {})
        bundle_budget = performance.get("bundle_budget", {})
        animation_budget = performance.get("animation_budget", {})
        performance_score_parts = [
            performance.get("lazy_loading") is True,
            isinstance(image_optimization, dict) and "webp" in image_optimization.get("formats", []),
            isinstance(image_optimization, dict) and image_optimization.get("responsive_images") is True,
            isinstance(bundle_budget, dict) and bundle_budget.get("max_js_kb", 9999) <= 300,
            isinstance(animation_budget, dict)
            and animation_budget.get("respect_prefers_reduced_motion") is True,
        ]
        performance_score = DesignPipelineNode._score_ratio(performance_score_parts)

        seo_requirements = [
            page.get("seo_requirements", {})
            for page in pages
            if isinstance(page, dict)
        ]
        seo_score_parts = [
            bool(seo_requirements),
            all(bool(seo.get("title")) for seo in seo_requirements),
            all(bool(seo.get("description")) for seo in seo_requirements),
            all(seo.get("og_image") is True for seo in seo_requirements),
        ]
        seo_score = DesignPipelineNode._score_ratio(seo_score_parts)

        enabled_resources = [
            resource
            for resource in resource_usage
            if isinstance(resource, dict) and resource.get("enabled")
        ]
        originality_score_parts = [
            len(section_layouts) >= 3,
            len(enabled_resources) >= 3,
            bool(interactions),
            any(
                section.get("motion")
                for section in sections
                if isinstance(section, dict)
            ),
        ]
        originality_score = DesignPipelineNode._score_ratio(originality_score_parts)

        return [
            ElevationSignal(
                "brand_alignment",
                brand_score,
                f"{sum(brand_score_parts)}/{len(brand_score_parts)} brand/token checks passed",
            ),
            ElevationSignal(
                "accessibility",
                accessibility_score,
                f"{sum(accessibility_score_parts)}/{len(accessibility_score_parts)} accessibility checks passed",
            ),
            ElevationSignal(
                "visual_craft",
                visual_score,
                f"{len(sections)} sections, {len(components)} components, {len(section_layouts)} layout types",
            ),
            ElevationSignal(
                "performance",
                performance_score,
                f"{sum(performance_score_parts)}/{len(performance_score_parts)} performance checks passed",
            ),
            ElevationSignal(
                "seo_impact",
                seo_score,
                f"{sum(seo_score_parts)}/{len(seo_score_parts)} SEO checks passed",
            ),
            ElevationSignal(
                "originality",
                originality_score,
                f"{len(section_layouts)} layout types, {len(enabled_resources)} enabled resources, {len(interactions)} interactions",
            ),
        ]

    @staticmethod
    def _score_ratio(checks: list[bool]) -> float:
        if not checks:
            return 0.0
        return round((sum(1 for check in checks if check) / len(checks)) * 100.0, 2)

    @staticmethod
    def _adapt_build_plan_for_site_builder(plan_dict: dict) -> dict:
        """
        Bridge two mismatches between design_execution_planner's
        DesignBuildPlan.to_dict() output and what site_builder's
        execute_build() actually consumes:

        1. Key naming: design_execution_planner emits "typography_plan",
           "layout_plan", "performance_plan", "accessibility_plan"; site_builder
           reads "typography", "layout", "performance", "accessibility"
           (no suffix). Non-destructive: original *_plan keys are kept too.

        2. implementation_order format (the bigger one): site_builder's
           execute_build() loops `for step in design_build_plan["implementation_order"]:
           self._execute_step(step, ...)`, and _execute_step does
           `if step == "dependencies": ...`comparing step directly against
           plain keyword strings. But design_execution_planner's
           implementation_order is a list of ImplementationStep *dicts*
           (`{"order": 1, "task": "Project setup", ...}`) - a dict can never
           equal a string, so every branch of that if/elif chain was always
           False and execute_build() silently did nothing for any plan,
           regardless of the key-naming fix above. This maps each step's
           free-text "task" description to the keyword site_builder's
           dispatcher expects via substring matching, and replaces
           implementation_order with that flat list of keywords. Steps that
           don't match any known keyword are dropped from the executable
           order but kept under "_unmapped_steps" for visibility/debugging
           instead of silently vanishing.
        """
        key_aliases = {
            "typography_plan": "typography",
            "layout_plan": "layout",
            "performance_plan": "performance",
            "accessibility_plan": "accessibility",
        }
        adapted = dict(plan_dict)
        for source_key, target_key in key_aliases.items():
            if source_key in plan_dict and target_key not in plan_dict:
                adapted[target_key] = plan_dict[source_key]

        keyword_hints = {
            "dependencies": ["depend"],
            "tokens": ["token"],
            "global_styles": ["global style", "global css"],
            "typography": ["typograph"],
            "layout": ["layout"],
            "navigation": ["navigation", "nav bar", "nav menu"],
            "sections": ["section"],
            "components": ["component"],
            "assets": ["asset", "image", "icon"],
            "interactions": ["interaction", "motion", "animation"],
            "responsive": ["responsive"],
            "accessibility": ["accessib"],
            "performance": ["performance"],
            "validation": ["valid"],
        }

        raw_steps = plan_dict.get("implementation_order", [])
        mapped_steps = []
        unmapped_steps = []
        for raw_step in raw_steps:
            task_text = ""
            if isinstance(raw_step, dict):
                task_text = str(raw_step.get("task", "")).lower()
            elif isinstance(raw_step, str):
                task_text = raw_step.lower()

            matched_keyword = None
            for keyword, hints in keyword_hints.items():
                if any(hint in task_text for hint in hints):
                    matched_keyword = keyword
                    break

            if matched_keyword:
                mapped_steps.append(matched_keyword)
            else:
                unmapped_steps.append(raw_step)

        # Multiple free-text tasks can map to the same dispatcher keyword
        # (e.g. both "Hero section" and "Content sections" map to
        # "sections"). Running the same step twice duplicates output
        # (site_builder would build every section twice) without adding
        # any value, since each _handle_* method already processes the
        # full corresponding list from design_build_plan in one pass.
        # Dedupe while preserving first-seen order.
        seen = set()
        deduped_steps = []
        for keyword in mapped_steps:
            if keyword not in seen:
                seen.add(keyword)
                deduped_steps.append(keyword)

        adapted["implementation_order"] = deduped_steps
        adapted["_unmapped_steps"] = unmapped_steps

        # 3. section_builder.build_section() expects section["layout"] and
        # section["motion"] to be dicts ({"type": "grid", ...} /
        # {"enabled": bool, "initial": {...}, ...}); SectionPlan.to_dict()
        # serializes layout as a plain string (LayoutType enum's .value)
        # and motion as a plain List[str] of effect names. Wrap both
        # non-destructively so site_builder gets the shape it reads
        # without changing what design_execution_planner produces.
        if "sections" in adapted and isinstance(adapted["sections"], list):
            def _adapt_section(s):
                if not isinstance(s, dict):
                    return s
                s = dict(s)
                if isinstance(s.get("layout"), str):
                    s["layout"] = {"type": s["layout"]}
                if isinstance(s.get("motion"), list):
                    effects = s["motion"]
                    s["motion"] = {
                        "enabled": len(effects) > 0,
                        "effects": effects,
                        "initial": {},
                        "animate": {},
                        "transition": {},
                    }
                if isinstance(s.get("responsive_behavior"), dict):
                    # planner.py currently hardcodes entries like
                    # {"mobile": "stack"} (a bare string) instead of the
                    # nested {"mobile": {"stack": True}} shape
                    # section_builder._build_responsive_classes() reads via
                    # mobile.get("stack"). ResponsivePlanner exists as its
                    # own module but isn't actually wired into planner.py's
                    # section generation yet (see PLAN.md) - this only
                    # bridges the shape of whatever string value is there
                    # today, it doesn't compute anything new.
                    fixed_responsive = {}
                    for breakpoint_key, value in s["responsive_behavior"].items():
                        if isinstance(value, str):
                            fixed_responsive[breakpoint_key] = {value: True}
                        else:
                            fixed_responsive[breakpoint_key] = value
                    s["responsive_behavior"] = fixed_responsive
                if isinstance(s.get("components"), list) and s["components"] and isinstance(s["components"][0], str):
                    # SectionPlan.components is List[str] of component
                    # names; section_builder._generate_component_imports()
                    # reads comp.get("name", ...) expecting dicts.
                    s["components"] = [{"name": c} for c in s["components"]]
                return s

            adapted["sections"] = [_adapt_section(s) for s in adapted["sections"]]

        return adapted

    @staticmethod
    def _failure(task_id: str, stage: str, error: Exception, stages: dict) -> dict:
        return {
            "node": "DesignPipelineNode",
            "task_id": task_id,
            "status": "failed",
            "failed_stage": stage,
            "error": str(error),
            "stages": stages,
        }
