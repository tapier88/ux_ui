"""
Design Pipeline Nodes — wires the 5 design skills into the graph engine.

Before this module existed, harness/nodes/ only had GitPersistenceNode:
every skill (Website Intelligence, Redesign Intelligence, Design
Resource Hub, Design Execution Planner, Site Builder) worked in
isolation and had to be called manually, one at a time, with the
person gluing the outputs together by hand. This module is what makes
ROADMAP.md FASE 1 (end-to-end orchestration) real: a single graph run
now takes a project on disk all the way to either a built redesign or a
clearly-recorded reason it was blocked.

See build_design_pipeline_graph() at the bottom for the assembled graph.

Data flow (state.outputs is keyed by node id, per harness/core/runtime):
    state.inputs["project_path"]         (required)
    state.inputs["url"]                  (optional, passed to inspector)
    state.inputs["skip_dependency_install"] (optional, default True —
        see SiteBuilderNode; real npm installs are opt-in, not automatic)
        ↓
    WEBSITE_INTELLIGENCE_NODE   -> profile dict
        ↓
    REDESIGN_INTELLIGENCE_NODE  -> strategy dict (uses profile)
        ↓
    DESIGN_RESOURCE_HUB_NODE    -> resource report dict (uses profile + strategy)
        ↓
    DESIGN_EXECUTION_PLANNER_NODE -> build plan dict (uses all of the above)
        ↓
    GOVERNANCE_GATE_NODE (CONDITIONAL) -> {"passed": bool, ...} + routes
        "approved" -> SITE_BUILDER_NODE -> END
        "blocked"  -> END directly (see ARCHITECTURE_PRINCIPLES.md §1/§5:
                       no skill output reaches Site Builder without
                       clearing the gate — this is what actually enforces
                       that rule at runtime, not just in a docstring)
"""
from typing import Any, Dict, List, Optional

from harness.core.graph import NodeType
from harness.core.state import TaskState
from harness.core.governance import ElevationSignal, GovernanceGate
from harness.nodes import BaseNode


class WebsiteIntelligenceNode(BaseNode):
    """Inspects the project on disk (and optionally a live URL) and
    produces a WebsiteDesignProfile dict."""

    def __init__(self, node_id: str = "WEBSITE_INTELLIGENCE_NODE"):
        super().__init__(node_id, "Website Intelligence", NodeType.STANDARD)
        self.execute_func = self.execute

    def execute(self, state: TaskState) -> Dict[str, Any]:
        from harness.skills.website_intelligence import analyze_website

        project_path = state.inputs.get("project_path")
        url = state.inputs.get("url")
        return analyze_website(project_path=project_path, url=url)


class RedesignIntelligenceNode(BaseNode):
    """Decides what to preserve/remove/improve, and generates a real
    color palette from the profile's brand color (see
    redesign_intelligence/color_intelligence.py)."""

    def __init__(self, node_id: str = "REDESIGN_INTELLIGENCE_NODE",
                 upstream_node_id: str = "WEBSITE_INTELLIGENCE_NODE"):
        super().__init__(node_id, "Redesign Intelligence", NodeType.STANDARD)
        self.upstream_node_id = upstream_node_id
        self.execute_func = self.execute

    def execute(self, state: TaskState) -> Dict[str, Any]:
        from harness.skills.redesign_intelligence.engine import RedesignIntelligenceEngine

        profile = dict(state.outputs.get(self.upstream_node_id, {}) or {})

        # --- Temporary adapter, remove once ROADMAP.md FASE 2B (Brand
        # DNA Extractor) exists ---
        # WebsiteDesignProfile (website_intelligence) has no top-level
        # "brand"/"colors" section — that's Brand DNA Extractor's job,
        # and it isn't built yet. Until then, derive the one signal we
        # can from what Website Intelligence actually inspects (the
        # dominant color already present in the site's own CSS) so
        # ColorStrategyEngine has a real, non-fabricated color to build
        # a palette from instead of silently producing nothing. This is
        # explicitly a lesser substitute — a single dominant CSS color
        # is not the same as a considered brand DNA extraction — and it
        # should be deleted, not extended, once FASE 2B lands.
        if "colors" not in profile or not profile.get("colors"):
            dominant = (
                (profile.get("visual_design") or {})
                .get("color_palette", {})
                .get("dominant_color")
            )
            if dominant:
                profile["colors"] = {"primary": dominant}

        strategy = RedesignIntelligenceEngine().analyze(profile)
        return strategy.to_dict()


class DesignResourceHubNode(BaseNode):
    """Selects real frameworks/libraries and consults design-methodology
    references, based on the profile + redesign strategy."""

    def __init__(self, node_id: str = "DESIGN_RESOURCE_HUB_NODE",
                 profile_node_id: str = "WEBSITE_INTELLIGENCE_NODE",
                 strategy_node_id: str = "REDESIGN_INTELLIGENCE_NODE"):
        super().__init__(node_id, "Design Resource Hub", NodeType.STANDARD)
        self.profile_node_id = profile_node_id
        self.strategy_node_id = strategy_node_id
        self.execute_func = self.execute

    def execute(self, state: TaskState) -> Dict[str, Any]:
        from harness.skills.design_resource_hub import (
            ResourceSelector,
            DesignResourceResearchRequest,
        )

        profile = state.outputs.get(self.profile_node_id, {}) or {}
        strategy = state.outputs.get(self.strategy_node_id, {}) or {}
        brand = profile.get("brand", {}) if isinstance(profile, dict) else {}

        request = DesignResourceResearchRequest(
            project_type=profile.get("project_type", "marketing_site"),
            industry=brand.get("industry", "general"),
            brand_personality=brand.get("personality", "professional"),
            visual_style=(strategy.get("visual_strategy", {}) or {}).get("style", "minimalist"),
            layout_style=(strategy.get("layout_strategy", {}) or {}).get("pattern", "standard"),
            animation_level=(strategy.get("motion_strategy", {}) or {}).get("level", "MEDIUM"),
            interaction_level=(strategy.get("motion_strategy", {}) or {}).get("interaction_level", "MEDIUM"),
        )

        selector = ResourceSelector()
        selected, rejected = selector.select_resources(request)
        report = selector.generate_report(request, task_id=state.task_id)
        return report.to_dict()


class DesignExecutionPlannerNode(BaseNode):
    """Converts profile + strategy + resource report into a technical
    build plan (layout, tokens, components, motion, responsive,
    accessibility, performance)."""

    def __init__(self, node_id: str = "DESIGN_EXECUTION_PLANNER_NODE",
                 profile_node_id: str = "WEBSITE_INTELLIGENCE_NODE",
                 strategy_node_id: str = "REDESIGN_INTELLIGENCE_NODE",
                 resource_node_id: str = "DESIGN_RESOURCE_HUB_NODE"):
        super().__init__(node_id, "Design Execution Planner", NodeType.STANDARD)
        self.profile_node_id = profile_node_id
        self.strategy_node_id = strategy_node_id
        self.resource_node_id = resource_node_id
        self.execute_func = self.execute

    def execute(self, state: TaskState) -> Dict[str, Any]:
        from harness.skills.design_execution_planner import DesignExecutionPlanner

        profile = state.outputs.get(self.profile_node_id, {})
        strategy = state.outputs.get(self.strategy_node_id, {})
        resource_report = state.outputs.get(self.resource_node_id, {})

        planner = DesignExecutionPlanner()
        plan = planner.create_build_plan(
            project_name=state.inputs.get("project_name", state.task_id),
            design_profile=profile,
            redesign_strategy=strategy,
            resource_report=resource_report,
        )
        return plan.to_dict()


class GovernanceGateNode(BaseNode):
    """Scores the plan against the Elevation Scorer and blocks the
    pipeline before Site Builder if it doesn't clear the threshold —
    see ARCHITECTURE_PRINCIPLES.md §1/§5. This is a CONDITIONAL node:
    its condition_func reads the score it just computed and routes to
    "approved" or "blocked".

    IMPORTANT — current limitation (tracked in ROADMAP.md): the
    signals scored here are still heuristic proxies (e.g. "did the
    color engine report full WCAG AA compliance"), not full real
    measurements like actual Core Web Vitals or a rendered-page
    contrast audit. Real signal wiring is the next task after this one.
    """

    def __init__(self, node_id: str = "GOVERNANCE_GATE_NODE",
                 plan_node_id: str = "DESIGN_EXECUTION_PLANNER_NODE",
                 strategy_node_id: str = "REDESIGN_INTELLIGENCE_NODE",
                 threshold: float = 60.0,
                 gate: Optional[GovernanceGate] = None):
        super().__init__(node_id, "Governance Gate", NodeType.CONDITIONAL)
        self.plan_node_id = plan_node_id
        self.strategy_node_id = strategy_node_id
        self.gate = gate or GovernanceGate(threshold=threshold)
        self.execute_func = self.execute
        self.condition_func = self._route

    def execute(self, state: TaskState) -> Dict[str, Any]:
        strategy = state.outputs.get(self.strategy_node_id, {}) or {}
        plan = state.outputs.get(self.plan_node_id, {}) or {}
        signals = self._derive_signals(strategy, plan)

        subject = state.inputs.get("project_name", state.task_id)
        result = self.gate.evaluate(signals, task_id=state.task_id, subject=subject)
        return result.to_dict()

    def _route(self, state: TaskState) -> str:
        result = state.outputs.get(self.id, {})
        return "approved" if result.get("passed") else "blocked"

    @staticmethod
    def _derive_signals(strategy: Dict[str, Any], plan: Dict[str, Any]) -> List[ElevationSignal]:
        color_strategy = strategy.get("color_strategy", {}) or {}
        contrast_report = {}  # not yet exposed on ColorStrategy.to_dict(); see note below
        accessibility_plan = plan.get("accessibility_plan", {}) or {}
        performance_plan = plan.get("performance_plan", {}) or {}

        # brand_alignment: did we actually anchor on a real brand color,
        # or fall back to nothing (see color_intelligence.py)?
        brand_alignment = 90.0 if color_strategy.get("primary") else 30.0

        # accessibility: proxy on whether an accessibility plan exists
        # and whether the color engine's own notes flagged unresolved
        # contrast issues.
        color_notes = color_strategy.get("recommendations", []) or []
        contrast_issue_flagged = any("does not meet AA" in note for note in color_notes)
        accessibility = 55.0 if contrast_issue_flagged else (85.0 if accessibility_plan else 50.0)

        # visual_craft: proxy on layout plan existing with a real pattern
        # (not the bare default) and design tokens being present.
        visual_craft = 80.0 if plan.get("layout_plan") and plan.get("design_tokens") else 45.0

        performance = 75.0 if performance_plan else 50.0
        seo_impact = 70.0  # placeholder until Website Intelligence exposes SEO metrics
        originality = 65.0  # placeholder until FASE 2B Brand DNA scoring exists

        return [
            ElevationSignal("brand_alignment", brand_alignment),
            ElevationSignal("accessibility", accessibility,
                             evidence="derived from color engine notes; not yet a full audit"),
            ElevationSignal("visual_craft", visual_craft),
            ElevationSignal("performance", performance),
            ElevationSignal("seo_impact", seo_impact),
            ElevationSignal("originality", originality),
        ]


class SiteBuilderNode(BaseNode):
    """Executes the build plan as real file changes on the project,
    with checkpoint/rollback safety (see site_builder/builder.py).

    Only reached if GovernanceGateNode routed to "approved" — the graph
    edges enforce this, not this node's own logic, but the node also
    checks defensively in case it's ever wired into a different graph.
    """

    def __init__(self, node_id: str = "SITE_BUILDER_NODE",
                 plan_node_id: str = "DESIGN_EXECUTION_PLANNER_NODE",
                 gate_node_id: str = "GOVERNANCE_GATE_NODE"):
        super().__init__(node_id, "Site Builder", NodeType.STANDARD)
        self.plan_node_id = plan_node_id
        self.gate_node_id = gate_node_id
        self.execute_func = self.execute

    # DesignExecutionPlanner produces a rich, human-readable
    # implementation_order (task descriptions like "Hero section",
    # "Quality validation") but SiteBuilder._execute_step() only
    # recognizes a fixed, short set of step ids ("tokens", "sections",
    # "validation", etc.) — these two skills were built independently
    # and this mismatch only surfaces when actually wired end-to-end
    # (see ROADMAP.md FASE 1). Translating here, at the point of
    # consumption, keeps the planner's richer output intact for anyone
    # inspecting the plan directly.
    _STEP_KEYWORD_MAP = [
        ("dependenc", "dependencies"),
        ("project setup", "dependencies"),
        ("token", "tokens"),
        ("typograph", "typography"),
        ("global", "global_styles"),
        ("layout", "layout"),
        ("navigation", "navigation"),
        ("hero", "sections"),
        ("content section", "sections"),
        ("section", "sections"),
        ("component", "components"),
        ("asset", "assets"),
        ("interaction", "interactions"),
        ("responsive", "responsive"),
        ("accessibility", "accessibility"),
        ("performance", "performance"),
        ("quality validation", "validation"),
        ("validation", "validation"),
    ]

    @classmethod
    def _translate_implementation_order(cls, raw_order: List[Any]) -> List[str]:
        """Translate DesignExecutionPlanner's task list into the flat
        step-id vocabulary SiteBuilder understands, preserving order and
        without duplicates."""
        translated: List[str] = []
        for entry in raw_order:
            label = entry.get("task", "") if isinstance(entry, dict) else str(entry)
            label_lower = label.lower()
            for keyword, step_id in cls._STEP_KEYWORD_MAP:
                if keyword in label_lower:
                    if step_id not in translated:
                        translated.append(step_id)
                    break
        return translated

    def execute(self, state: TaskState) -> Dict[str, Any]:
        from harness.skills.site_builder import SiteBuilder
        from harness.skills.site_builder.models import ValidationStatus

        gate_result = state.outputs.get(self.gate_node_id, {})
        if gate_result and not gate_result.get("passed", False):
            # Defensive guard — should be unreachable via the intended
            # graph wiring (see build_design_pipeline_graph), but never
            # silently build on a blocked plan if reached some other way.
            raise RuntimeError(
                "SiteBuilderNode reached with a blocked GovernanceGate result "
                "— refusing to write real file changes. Check graph wiring."
            )

        project_path = state.inputs.get("project_path")
        if not project_path:
            raise ValueError("SiteBuilderNode requires state.inputs['project_path']")

        plan = state.outputs.get(self.plan_node_id, {})
        implementation_order = self._translate_implementation_order(
            plan.get("implementation_order", [])
        )

        # Real npm installs are opt-in, not automatic, during an
        # unsupervised pipeline run — see module docstring.
        skip_dependency_install = state.inputs.get("skip_dependency_install", True)
        if skip_dependency_install:
            implementation_order = [s for s in implementation_order if s != "dependencies"]

        plan = {**plan, "implementation_order": implementation_order}

        builder = SiteBuilder(project_path)
        report = builder.execute_build(plan)

        if report.build_status != ValidationStatus.PASS:
            # Match CRITICAL-005's philosophy at the pipeline level too:
            # a build that internally failed (and rolled back) must make
            # this NODE fail, not just report failure inside a dict the
            # runtime has no reason to inspect. Without this, the graph
            # runtime would mark the whole task "completed" even though
            # the actual file changes never landed — the exact bug this
            # project's Fase 0 fixed in the runtime itself.
            raise RuntimeError(
                f"Site Builder failed: {report.errors or 'unknown error'} "
                f"(rollback status: {report.rollback_status})"
            )

        return report.to_dict()


def build_design_pipeline_graph(governance_threshold: float = 60.0):
    """Assemble the full graph: Website Intelligence -> Redesign
    Intelligence -> Design Resource Hub -> Design Execution Planner ->
    Governance Gate -> (approved: Site Builder | blocked: END).

    Built with the low-level Graph API rather than GraphBuilder: this
    graph has a real fork (the gate's two conditional edges), which
    GraphBuilder's fluent single-`_last_node` tracking isn't designed
    for — using it here would silently mis-wire START/END connections.
    """
    from harness.core.graph import Graph, Node, Edge

    graph = Graph("design_pipeline")

    start = Node(id="START", name="Start", node_type=NodeType.START)
    end = Node(id="END", name="End", node_type=NodeType.END)

    wi = WebsiteIntelligenceNode()
    ri = RedesignIntelligenceNode()
    drh = DesignResourceHubNode()
    dep = DesignExecutionPlannerNode()
    gate = GovernanceGateNode(threshold=governance_threshold)
    sb = SiteBuilderNode()

    for node in (start, wi, ri, drh, dep, gate, sb, end):
        graph.add_node(node)

    graph.add_edge(Edge(source="START", target=wi.id))
    graph.add_edge(Edge(source=wi.id, target=ri.id))
    graph.add_edge(Edge(source=ri.id, target=drh.id))
    graph.add_edge(Edge(source=drh.id, target=dep.id))
    graph.add_edge(Edge(source=dep.id, target=gate.id))
    graph.add_edge(Edge(source=gate.id, target=sb.id, condition="approved"))
    graph.add_edge(Edge(source=gate.id, target="END", condition="blocked"))
    graph.add_edge(Edge(source=sb.id, target="END"))

    return graph
