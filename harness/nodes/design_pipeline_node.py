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

        if dry_run:
            return {
                "node": "DesignPipelineNode",
                "task_id": state.task_id,
                "status": "dry_run_completed",
                "stages": stages,
                "build_plan": build_plan.to_dict(),
            }

        # 5. Site Builder - actually write the code changes
        try:
            from harness.skills.site_builder import SiteBuilder

            builder = SiteBuilder(project_path)
            report = builder.execute_build(build_plan)
            stages["site_builder"] = {"status": "completed"}
        except Exception as e:
            return self._failure(state.task_id, "site_builder", e, stages)

        return {
            "node": "DesignPipelineNode",
            "task_id": state.task_id,
            "status": "completed",
            "stages": stages,
            "report": report.to_dict(),
        }

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
