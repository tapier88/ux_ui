"""
Deterministic design agent cycle.

This is the first Fase 3 layer above the fixed DesignPipelineNode. It does not
introduce an LLM dependency yet; instead, it makes the agent loop explicit and
auditable:

    PLAN -> EXECUTE -> OBSERVE -> EVALUATE -> DECIDE

The first iteration always executes the pipeline in dry-run mode, observes the
build plan and governance result, evaluates whether it is safe to write, and
decides whether to stop, wait for execution approval, or run the real build.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from harness.core.state import TaskState
from harness.core.time import utc_now_iso
from harness.nodes.design_pipeline_node import DesignPipelineNode


class AgentDecision:
    """Stable decision labels returned by the deterministic design cycle."""

    BLOCKED = "blocked"
    READY_TO_EXECUTE = "ready_to_execute"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class AgentCycleStep:
    """One auditable step in the agent loop."""

    phase: str
    status: str
    summary: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status,
            "summary": self.summary,
            "data": self.data,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentCycleResult:
    """Result of one deterministic agent run."""

    task_id: str
    decision: str
    trace: List[AgentCycleStep] = field(default_factory=list)
    dry_run_result: Optional[Dict[str, Any]] = None
    build_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "decision": self.decision,
            "trace": [step.to_dict() for step in self.trace],
            "dry_run_result": self.dry_run_result,
            "build_result": self.build_result,
        }


class DeterministicDesignAgent:
    """Runs DesignPipelineNode through an explicit agent decision cycle."""

    def __init__(self, pipeline_node: Optional[DesignPipelineNode] = None):
        self.pipeline_node = pipeline_node or DesignPipelineNode()

    def run(
        self,
        project_path: str,
        task_id: str = "design-agent-cycle",
        url: Optional[str] = None,
        resource_hub_options: Optional[Dict[str, Any]] = None,
        execute: bool = False,
        governance_threshold: float = 75.0,
    ) -> AgentCycleResult:
        trace: List[AgentCycleStep] = []

        trace.append(
            AgentCycleStep(
                phase="PLAN",
                status="completed",
                summary="Prepared dry-run pipeline inputs before any disk write.",
                data={
                    "project_path": project_path,
                    "url": url,
                    "execute_requested": execute,
                    "governance_threshold": governance_threshold,
                },
            )
        )

        dry_run_result = self._run_pipeline(
            task_id=f"{task_id}:dry-run",
            project_path=project_path,
            url=url,
            resource_hub_options=resource_hub_options,
            dry_run=True,
            governance_threshold=governance_threshold,
        )
        trace.append(
            AgentCycleStep(
                phase="EXECUTE",
                status=dry_run_result.get("status", "unknown"),
                summary="Executed planning pipeline in dry-run mode.",
                data={"mode": "dry_run"},
            )
        )

        observation = self._observe_pipeline_result(dry_run_result)
        trace.append(
            AgentCycleStep(
                phase="OBSERVE",
                status="completed",
                summary="Observed stage statuses and governance output.",
                data=observation,
            )
        )

        evaluation = self._evaluate_observation(observation)
        trace.append(
            AgentCycleStep(
                phase="EVALUATE",
                status="completed" if evaluation["passed"] else "blocked",
                summary=evaluation["summary"],
                data=evaluation,
            )
        )

        if not evaluation["passed"]:
            trace.append(
                AgentCycleStep(
                    phase="DECIDE",
                    status=AgentDecision.BLOCKED,
                    summary="Stopped before build because evaluation failed.",
                    data={"reason": evaluation["summary"]},
                )
            )
            return AgentCycleResult(
                task_id=task_id,
                decision=AgentDecision.BLOCKED,
                trace=trace,
                dry_run_result=dry_run_result,
            )

        if not execute:
            trace.append(
                AgentCycleStep(
                    phase="DECIDE",
                    status=AgentDecision.READY_TO_EXECUTE,
                    summary="Dry run passed; waiting for explicit execute=True to write files.",
                    data={"requires_execute": True},
                )
            )
            return AgentCycleResult(
                task_id=task_id,
                decision=AgentDecision.READY_TO_EXECUTE,
                trace=trace,
                dry_run_result=dry_run_result,
            )

        trace.append(
            AgentCycleStep(
                phase="DECIDE",
                status="approved_for_execution",
                summary="Dry run passed and execute=True was requested; starting real build.",
            )
        )

        build_result = self._run_pipeline(
            task_id=f"{task_id}:build",
            project_path=project_path,
            url=url,
            resource_hub_options=resource_hub_options,
            dry_run=False,
            governance_threshold=governance_threshold,
        )
        trace.append(
            AgentCycleStep(
                phase="EXECUTE",
                status=build_result.get("status", "unknown"),
                summary="Executed real build pipeline.",
                data={"mode": "real_build"},
            )
        )

        build_observation = self._observe_pipeline_result(build_result)
        trace.append(
            AgentCycleStep(
                phase="OBSERVE",
                status="completed",
                summary="Observed real build result.",
                data=build_observation,
            )
        )

        build_evaluation = self._evaluate_build_result(build_result)
        trace.append(
            AgentCycleStep(
                phase="EVALUATE",
                status="completed" if build_evaluation["passed"] else "failed",
                summary=build_evaluation["summary"],
                data=build_evaluation,
            )
        )

        final_decision = (
            AgentDecision.COMPLETE if build_evaluation["passed"] else AgentDecision.FAILED
        )
        trace.append(
            AgentCycleStep(
                phase="DECIDE",
                status=final_decision,
                summary=(
                    "Build completed successfully."
                    if final_decision == AgentDecision.COMPLETE
                    else "Build failed or was blocked."
                ),
            )
        )

        return AgentCycleResult(
            task_id=task_id,
            decision=final_decision,
            trace=trace,
            dry_run_result=dry_run_result,
            build_result=build_result,
        )

    def _run_pipeline(
        self,
        task_id: str,
        project_path: str,
        url: Optional[str],
        resource_hub_options: Optional[Dict[str, Any]],
        dry_run: bool,
        governance_threshold: float,
    ) -> Dict[str, Any]:
        state = TaskState(task_id=task_id)
        state.inputs = {
            "project_path": project_path,
            "url": url,
            "resource_hub_options": resource_hub_options or {},
            "dry_run": dry_run,
            "governance_threshold": governance_threshold,
            "governance_record_to_memory": False,
        }
        return self.pipeline_node.execute(state)

    @staticmethod
    def _observe_pipeline_result(result: Dict[str, Any]) -> Dict[str, Any]:
        stages = result.get("stages", {})
        return {
            "pipeline_status": result.get("status"),
            "stage_statuses": {
                name: stage.get("status")
                for name, stage in stages.items()
                if isinstance(stage, dict)
            },
            "governance": result.get("governance"),
            "failed_stage": result.get("failed_stage"),
            "build_status": (result.get("report") or {}).get("build_status"),
            "errors": (result.get("report") or {}).get("errors", []),
        }

    @staticmethod
    def _evaluate_observation(observation: Dict[str, Any]) -> Dict[str, Any]:
        governance = observation.get("governance") or {}
        stage_statuses = observation.get("stage_statuses", {})

        failed_stages = [
            name
            for name, status in stage_statuses.items()
            if status not in ("completed",)
        ]
        if failed_stages:
            return {
                "passed": False,
                "summary": f"Stages did not complete cleanly: {', '.join(failed_stages)}",
                "failed_stages": failed_stages,
            }
        if not governance.get("passed"):
            return {
                "passed": False,
                "summary": "Governance gate did not pass.",
                "governance": governance,
            }
        return {
            "passed": True,
            "summary": "Dry-run pipeline and governance passed.",
            "governance": governance,
        }

    @staticmethod
    def _evaluate_build_result(result: Dict[str, Any]) -> Dict[str, Any]:
        report = result.get("report") or {}
        errors = report.get("errors", [])
        if result.get("status") != "completed":
            return {
                "passed": False,
                "summary": f"Pipeline status is {result.get('status')}.",
                "failed_stage": result.get("failed_stage"),
            }
        if errors:
            return {
                "passed": False,
                "summary": f"Build reported {len(errors)} errors.",
                "errors": errors,
            }
        if report.get("build_status") != "pass":
            return {
                "passed": False,
                "summary": f"Build status is {report.get('build_status')}.",
            }
        return {
            "passed": True,
            "summary": "Real build completed with passing build status and no errors.",
        }
