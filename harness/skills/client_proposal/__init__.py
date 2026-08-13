"""
Client proposal generator.

Builds a concise client-facing before/after proposal from pipeline outputs. The
output is deterministic Markdown plus structured highlights that can later be
sent by email, CRM, or messaging connectors.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ClientProposal:
    title: str
    summary: str
    before_points: List[str] = field(default_factory=list)
    after_points: List[str] = field(default_factory=list)
    seo_impact: List[str] = field(default_factory=list)
    proof_points: List[str] = field(default_factory=list)
    markdown: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "before_points": self.before_points,
            "after_points": self.after_points,
            "seo_impact": self.seo_impact,
            "proof_points": self.proof_points,
            "markdown": self.markdown,
        }


class ClientProposalGenerator:
    """Generate a client-facing proposal from deterministic pipeline data."""

    def generate(
        self,
        profile: Optional[Dict[str, Any]] = None,
        build_plan: Optional[Dict[str, Any]] = None,
        seo: Optional[Dict[str, Any]] = None,
        governance: Optional[Dict[str, Any]] = None,
    ) -> ClientProposal:
        profile = profile or {}
        build_plan = build_plan or {}
        seo = seo or {}
        governance = governance or {}

        project_name = profile.get("project_name") or "your website"
        title = f"Redesign proposal for {project_name}"
        sections = build_plan.get("sections", [])
        components = build_plan.get("components", [])

        before_points = self._before_points(profile)
        after_points = [
            f"Rebuild the page around {len(sections)} purposeful sections.",
            f"Create or refine {len(components)} reusable interface components.",
            "Add explicit navigation, interaction, accessibility, and performance plans.",
        ]
        seo_impact = self._seo_impact(seo)
        proof_points = self._proof_points(governance)
        summary = (
            "This proposal turns the current site audit into a safer, more "
            "credible redesign plan with measurable quality gates before build."
        )
        markdown = self._markdown(
            title=title,
            summary=summary,
            before_points=before_points,
            after_points=after_points,
            seo_impact=seo_impact,
            proof_points=proof_points,
        )

        return ClientProposal(
            title=title,
            summary=summary,
            before_points=before_points,
            after_points=after_points,
            seo_impact=seo_impact,
            proof_points=proof_points,
            markdown=markdown,
        )

    def _before_points(self, profile: Dict[str, Any]) -> List[str]:
        points = []
        if not profile.get("visual_design"):
            points.append("Visual direction is not clearly detectable from the current codebase.")
        if not profile.get("accessibility"):
            points.append("Accessibility readiness is not explicit in the current audit.")
        if not profile.get("performance"):
            points.append("Performance readiness is not explicit in the current audit.")
        return points or ["The existing site has useful assets, but the redesign opportunity is structural."]

    def _seo_impact(self, seo: Dict[str, Any]) -> List[str]:
        score = seo.get("score", 0)
        checks = seo.get("checks", [])
        passed = sum(1 for check in checks if check.get("passed"))
        total = len(checks)
        impact = [f"SEO readiness score: {score}/100 ({passed}/{total} checks passed)."]
        for recommendation in seo.get("recommendations", [])[:3]:
            impact.append(recommendation)
        return impact

    def _proof_points(self, governance: Dict[str, Any]) -> List[str]:
        total_score = governance.get("total_score", 0)
        passed = governance.get("passed", False)
        status = "passed" if passed else "needs revision"
        points = [f"Governance gate {status} with score {total_score}/100."]
        for signal in governance.get("signals", [])[:4]:
            if isinstance(signal, dict):
                points.append(
                    f"{signal.get('name')}: {signal.get('score')}/100 - {signal.get('evidence')}"
                )
        return points

    def _markdown(
        self,
        title: str,
        summary: str,
        before_points: List[str],
        after_points: List[str],
        seo_impact: List[str],
        proof_points: List[str],
    ) -> str:
        def bullets(items: List[str]) -> str:
            return "\n".join(f"- {item}" for item in items)

        return "\n\n".join(
            [
                f"# {title}",
                summary,
                "## Before\n" + bullets(before_points),
                "## After\n" + bullets(after_points),
                "## SEO impact\n" + bullets(seo_impact),
                "## Quality proof\n" + bullets(proof_points),
            ]
        )


def client_proposal_skill(
    profile: Optional[Dict[str, Any]] = None,
    build_plan: Optional[Dict[str, Any]] = None,
    seo: Optional[Dict[str, Any]] = None,
    governance: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return ClientProposalGenerator().generate(
        profile=profile,
        build_plan=build_plan,
        seo=seo,
        governance=governance,
    ).to_dict()


__all__ = [
    "ClientProposal",
    "ClientProposalGenerator",
    "client_proposal_skill",
]
