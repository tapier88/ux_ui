# projects/

Standard destination for websites the agent generates or modifies via
`DesignPipelineNode` (`harness/nodes/design_pipeline_node.py`).

Each subdirectory here is a real `project_path` passed to the pipeline -
the actual project files the 5-stage pipeline (website_intelligence →
redesign_intelligence → design_resource_hub → design_execution_planner →
site_builder) inspects and writes to.

This directory is intentionally kept out of version control (see
`.gitignore`) - the generated project code isn't harness source, it's
output. If you need a fixed, reproducible project to test the pipeline
against, use `harness/tests/fixtures/sample_project/` instead, which *is*
checked in for that purpose (see `PLAN.md` Fase 2).
