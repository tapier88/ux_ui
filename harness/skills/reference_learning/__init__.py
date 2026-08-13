"""
Reference learning skill.

Turns external design/code references supplied by a caller into reusable design
lessons. This is deliberately connector-agnostic: scraping, GitHub, Figma, or
curated catalogs can provide references later without changing this contract.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReferenceLesson:
    pattern: str
    applicability: float
    evidence: str
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern": self.pattern,
            "applicability": self.applicability,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass
class ReferenceLearningReport:
    lessons: List[ReferenceLesson] = field(default_factory=list)
    references_used: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lessons": [lesson.to_dict() for lesson in self.lessons],
            "references_used": self.references_used,
        }


class ReferenceLearningEngine:
    """Extracts reusable lessons from supplied references."""

    PATTERNS = {
        "social_proof": ["testimonial", "case study", "review", "logo cloud"],
        "conversion_cta": ["cta", "book now", "schedule", "buy", "contact"],
        "visual_depth": ["gradient", "shadow", "layer", "card"],
        "accessibility": ["keyboard", "contrast", "aria", "reduced motion"],
        "performance": ["lazy", "webp", "bundle", "prefetch"],
    }

    def learn(
        self,
        references: Optional[List[Dict[str, Any]]] = None,
        project_context: Optional[Dict[str, Any]] = None,
    ) -> ReferenceLearningReport:
        references = references or []
        project_context = project_context or {}
        lessons = []
        for pattern, keywords in self.PATTERNS.items():
            evidence_refs = self._matching_references(references, keywords)
            if not evidence_refs:
                continue
            applicability = self._applicability(pattern, evidence_refs, project_context)
            lessons.append(
                ReferenceLesson(
                    pattern=pattern,
                    applicability=applicability,
                    evidence=self._evidence_summary(evidence_refs),
                    recommendation=self._recommendation(pattern),
                )
            )
        lessons.sort(key=lambda lesson: lesson.applicability, reverse=True)
        return ReferenceLearningReport(
            lessons=lessons,
            references_used=len(references),
        )

    def _matching_references(
        self,
        references: List[Dict[str, Any]],
        keywords: List[str],
    ) -> List[Dict[str, Any]]:
        matches = []
        for reference in references:
            haystack = " ".join(
                [
                    str(reference.get("title", "")),
                    str(reference.get("summary", "")),
                    " ".join(str(item) for item in reference.get("tags", [])),
                ]
            ).lower()
            if any(keyword in haystack for keyword in keywords):
                matches.append(reference)
        return matches

    def _applicability(
        self,
        pattern: str,
        references: List[Dict[str, Any]],
        project_context: Dict[str, Any],
    ) -> float:
        base = min(100.0, 45.0 + len(references) * 20.0)
        project_type = str(project_context.get("project_type", "")).lower()
        if pattern == "conversion_cta" and project_type in {"landing", "marketing", "local_business"}:
            base += 15.0
        if pattern == "social_proof" and project_type in {"landing", "local_business"}:
            base += 10.0
        return round(min(base, 100.0), 2)

    def _evidence_summary(self, references: List[Dict[str, Any]]) -> str:
        titles = [reference.get("title") or reference.get("url") or "untitled" for reference in references[:3]]
        return f"matched {len(references)} references: {', '.join(titles)}"

    def _recommendation(self, pattern: str) -> str:
        recommendations = {
            "social_proof": "Add proof sections using testimonials, logos, or short case-study snippets.",
            "conversion_cta": "Make the primary conversion action visible in hero, navigation, and final CTA.",
            "visual_depth": "Use restrained depth, cards, gradients, or layered sections to improve perceived craft.",
            "accessibility": "Carry accessibility tactics from references into focus, contrast, semantics, and motion.",
            "performance": "Adopt lightweight performance patterns such as responsive images and lazy loading.",
        }
        return recommendations[pattern]


def reference_learning_skill(
    references: Optional[List[Dict[str, Any]]] = None,
    project_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return ReferenceLearningEngine().learn(
        references=references,
        project_context=project_context,
    ).to_dict()


__all__ = [
    "ReferenceLearningEngine",
    "ReferenceLearningReport",
    "ReferenceLesson",
    "reference_learning_skill",
]
