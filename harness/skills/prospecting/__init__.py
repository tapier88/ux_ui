"""
Prospecting skill.

Local-first candidate scoring for finding websites that are likely worth a
redesign pitch. It does not scrape or contact anyone; it ranks provided
candidates using explicit, auditable signals.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProspectSignal:
    name: str
    score: float
    evidence: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "score": self.score,
            "evidence": self.evidence,
        }


@dataclass
class ProspectCandidate:
    url: str
    business_name: str
    score: float
    signals: List[ProspectSignal] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "business_name": self.business_name,
            "score": self.score,
            "signals": [signal.to_dict() for signal in self.signals],
            "reasons": self.reasons,
        }


class ProspectingEngine:
    """Ranks candidate websites by redesign opportunity."""

    WEIGHTS = {
        "outdated_stack": 0.25,
        "weak_mobile": 0.20,
        "weak_seo": 0.20,
        "weak_accessibility": 0.20,
        "business_fit": 0.15,
    }

    def rank(
        self,
        candidates: List[Dict[str, Any]],
        limit: Optional[int] = None,
    ) -> List[ProspectCandidate]:
        ranked = [self.score_candidate(candidate) for candidate in candidates]
        ranked.sort(key=lambda candidate: candidate.score, reverse=True)
        return ranked[:limit] if limit else ranked

    def score_candidate(self, candidate: Dict[str, Any]) -> ProspectCandidate:
        signals = [
            self._outdated_stack(candidate),
            self._weak_mobile(candidate),
            self._weak_seo(candidate),
            self._weak_accessibility(candidate),
            self._business_fit(candidate),
        ]
        score = round(
            sum(signal.score * self.WEIGHTS[signal.name] for signal in signals),
            2,
        )
        reasons = [
            signal.evidence for signal in signals if signal.score >= 70.0
        ]
        return ProspectCandidate(
            url=candidate.get("url", ""),
            business_name=candidate.get("business_name")
            or candidate.get("name")
            or "unknown",
            score=score,
            signals=signals,
            reasons=reasons,
        )

    def _outdated_stack(self, candidate: Dict[str, Any]) -> ProspectSignal:
        stack = [str(item).lower() for item in candidate.get("stack", [])]
        legacy_markers = {"jquery", "bootstrap 3", "wordpress classic", "table layout"}
        matches = sorted(marker for marker in legacy_markers if marker in stack)
        score = 100.0 if matches else 30.0
        return ProspectSignal(
            "outdated_stack",
            score,
            f"legacy stack markers: {', '.join(matches) if matches else 'none'}",
        )

    def _weak_mobile(self, candidate: Dict[str, Any]) -> ProspectSignal:
        mobile_score = float(candidate.get("mobile_score", 100.0))
        score = max(0.0, min(100.0, 100.0 - mobile_score))
        return ProspectSignal(
            "weak_mobile",
            score,
            f"mobile weakness score from reported mobile_score={mobile_score}",
        )

    def _weak_seo(self, candidate: Dict[str, Any]) -> ProspectSignal:
        seo_score = float(candidate.get("seo_score", 100.0))
        score = max(0.0, min(100.0, 100.0 - seo_score))
        return ProspectSignal(
            "weak_seo",
            score,
            f"SEO weakness score from reported seo_score={seo_score}",
        )

    def _weak_accessibility(self, candidate: Dict[str, Any]) -> ProspectSignal:
        accessibility_score = float(candidate.get("accessibility_score", 100.0))
        score = max(0.0, min(100.0, 100.0 - accessibility_score))
        return ProspectSignal(
            "weak_accessibility",
            score,
            f"accessibility weakness score from reported accessibility_score={accessibility_score}",
        )

    def _business_fit(self, candidate: Dict[str, Any]) -> ProspectSignal:
        industry = str(candidate.get("industry", "")).lower()
        priority = {"restaurant", "clinic", "law", "real estate", "local service"}
        score = 90.0 if industry in priority else 50.0 if industry else 30.0
        return ProspectSignal(
            "business_fit",
            score,
            f"industry fit: {industry or 'unknown'}",
        )


def prospecting_skill(
    candidates: Optional[List[Dict[str, Any]]] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    ranked = ProspectingEngine().rank(candidates or [], limit=limit)
    return {
        "candidates": [candidate.to_dict() for candidate in ranked],
        "count": len(ranked),
    }


__all__ = [
    "ProspectCandidate",
    "ProspectSignal",
    "ProspectingEngine",
    "prospecting_skill",
]
