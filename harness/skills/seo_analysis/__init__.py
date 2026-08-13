"""
SEO Analysis skill.

Deterministic, local-first SEO checks for the design pipeline. It does not call
external services; it evaluates metadata readiness, social preview coverage,
semantic structure, indexability hints, and performance support from the current
profile/build plan/project files.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SEOCheck:
    name: str
    passed: bool
    evidence: str
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class SEOAnalysisReport:
    score: float
    checks: List[SEOCheck] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "checks": [check.to_dict() for check in self.checks],
            "recommendations": self.recommendations,
        }


class SEOAnalysisEngine:
    """Runs deterministic SEO checks against pipeline data."""

    def analyze(
        self,
        profile: Optional[Dict[str, Any]] = None,
        build_plan: Optional[Dict[str, Any]] = None,
        project_path: Optional[str] = None,
    ) -> SEOAnalysisReport:
        profile = profile or {}
        build_plan = build_plan or {}
        checks = [
            self._check_titles(build_plan),
            self._check_descriptions(build_plan),
            self._check_social_preview(build_plan),
            self._check_semantic_structure(build_plan),
            self._check_performance_support(build_plan, profile),
            self._check_indexability(project_path),
        ]
        score = round(
            (sum(1 for check in checks if check.passed) / len(checks)) * 100.0,
            2,
        )
        recommendations = [
            check.recommendation for check in checks if not check.passed and check.recommendation
        ]
        return SEOAnalysisReport(score=score, checks=checks, recommendations=recommendations)

    def _page_seo(self, build_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        pages = build_plan.get("pages", [])
        return [
            page.get("seo_requirements", {})
            for page in pages
            if isinstance(page, dict)
        ]

    def _check_titles(self, build_plan: Dict[str, Any]) -> SEOCheck:
        seo_items = self._page_seo(build_plan)
        passed = bool(seo_items) and all(bool(item.get("title")) for item in seo_items)
        return SEOCheck(
            "page_titles",
            passed,
            f"{sum(1 for item in seo_items if item.get('title'))}/{len(seo_items)} pages include titles",
            "Add a unique SEO title for every planned page.",
        )

    def _check_descriptions(self, build_plan: Dict[str, Any]) -> SEOCheck:
        seo_items = self._page_seo(build_plan)
        passed = bool(seo_items) and all(bool(item.get("description")) for item in seo_items)
        return SEOCheck(
            "meta_descriptions",
            passed,
            f"{sum(1 for item in seo_items if item.get('description'))}/{len(seo_items)} pages include descriptions",
            "Add a concise meta description for every planned page.",
        )

    def _check_social_preview(self, build_plan: Dict[str, Any]) -> SEOCheck:
        seo_items = self._page_seo(build_plan)
        passed = bool(seo_items) and all(item.get("og_image") is True for item in seo_items)
        return SEOCheck(
            "social_preview",
            passed,
            f"{sum(1 for item in seo_items if item.get('og_image') is True)}/{len(seo_items)} pages include OG image intent",
            "Define Open Graph image coverage for every key page.",
        )

    def _check_semantic_structure(self, build_plan: Dict[str, Any]) -> SEOCheck:
        sections = build_plan.get("sections", [])
        has_sections = bool(sections)
        named_sections = [
            section for section in sections if isinstance(section, dict) and section.get("name")
        ]
        passed = has_sections and len(named_sections) == len(sections)
        return SEOCheck(
            "semantic_sections",
            passed,
            f"{len(named_sections)}/{len(sections)} sections have semantic names",
            "Ensure every page section has a semantic purpose/name.",
        )

    def _check_performance_support(
        self,
        build_plan: Dict[str, Any],
        profile: Dict[str, Any],
    ) -> SEOCheck:
        performance = build_plan.get("performance_plan", {})
        profile_performance = profile.get("performance") or {}
        passed = (
            performance.get("lazy_loading") is True
            or profile_performance.get("lighthouse_score", 0) >= 85
        )
        return SEOCheck(
            "performance_support",
            passed,
            "lazy loading planned or existing Lighthouse score is strong",
            "Add image lazy loading and keep Core Web Vitals budgets explicit.",
        )

    def _check_indexability(self, project_path: Optional[str]) -> SEOCheck:
        if not project_path:
            return SEOCheck(
                "indexability_hints",
                False,
                "no project path provided",
                "Provide a project path so robots/sitemap hints can be inspected.",
            )

        root = Path(project_path)
        robots = root / "robots.txt"
        public_robots = root / "public" / "robots.txt"
        sitemap = root / "sitemap.xml"
        public_sitemap = root / "public" / "sitemap.xml"
        passed = any(path.exists() for path in (robots, public_robots, sitemap, public_sitemap))
        return SEOCheck(
            "indexability_hints",
            passed,
            "robots.txt or sitemap.xml found" if passed else "no robots.txt or sitemap.xml found",
            "Add robots.txt or sitemap.xml for crawler guidance.",
        )


def seo_analysis_skill(
    profile: Optional[Dict[str, Any]] = None,
    build_plan: Optional[Dict[str, Any]] = None,
    project_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Skill entrypoint for registry and pipeline use."""
    return SEOAnalysisEngine().analyze(
        profile=profile,
        build_plan=build_plan,
        project_path=project_path,
    ).to_dict()


__all__ = [
    "SEOAnalysisEngine",
    "SEOAnalysisReport",
    "SEOCheck",
    "seo_analysis_skill",
]
