"""
Governance — Elevation Scorer + Gate

Design quality gate for this web-design agent. The scoring/threshold
pattern here (weighted signals, only proceed above a threshold, hard
floor per dimension) follows a general engineering principle documented
in ARCHITECTURE_PRINCIPLES.md §5: a model's raw creative output is never
executed directly — it always passes through a deterministic scoring
gate first.

Design:   brand_alignment (+30) + accessibility (+20) + visual_craft (+20)
          + performance (+15) + seo_impact (+10) + originality (+5)
          = weighted score → only ship if score >= threshold.

No skill in this harness should hand a redesign to the client (or to
Site Builder for a real commit) without passing through
GovernanceGate.evaluate(). This is a hard architectural rule, not a
suggestion — see ARCHITECTURE_PRINCIPLES.md §1 and §5.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from harness.core.events import EventType, emit_event
from harness.memory import MemoryCategory, MemoryStore, get_memory_store


# Default weights — configurable, not hardcoded logic. Callers should
# treat this as the starting point, not a fixed constant — see
# ARCHITECTURE_PRINCIPLES.md §6.
DEFAULT_ELEVATION_WEIGHTS: Dict[str, float] = {
    "brand_alignment": 30.0,   # does it still feel like THIS client's brand?
    "accessibility": 20.0,     # WCAG contrast, semantic structure, focus states
    "visual_craft": 20.0,      # real design-system execution vs generic template
    "performance": 15.0,       # Core Web Vitals / load characteristics
    "seo_impact": 10.0,        # preserved/improved structure, metadata
    "originality": 5.0,        # distance from generic AI-template patterns
}

# A signal below this value is treated as a hard fail for that dimension,
# regardless of the total weighted score — e.g. a broken contrast ratio
# cannot be offset by a great color palette elsewhere. Some conditions
# block outright, with no averaging — see ARCHITECTURE_PRINCIPLES.md §5.
HARD_FAIL_FLOOR = 40.0


@dataclass
class ElevationSignal:
    """A single scored dimension of a redesign, on a 0-100 scale.

    ``evidence`` should hold enough detail to make the score auditable
    later (e.g. which contrast ratios failed, which brand color was
    dropped) — this is what makes GATE_BLOCKED events useful instead of
    just a number.
    """
    name: str
    score: float  # 0-100
    evidence: Optional[str] = None

    def __post_init__(self):
        if not (0.0 <= self.score <= 100.0):
            raise ValueError(f"ElevationSignal '{self.name}' score must be 0-100, got {self.score}")


@dataclass
class ElevationResult:
    total_score: float
    weighted_breakdown: Dict[str, float]
    hard_fails: List[str] = field(default_factory=list)
    passed: bool = False

    def to_dict(self) -> Dict:
        return {
            "total_score": self.total_score,
            "weighted_breakdown": self.weighted_breakdown,
            "hard_fails": self.hard_fails,
            "passed": self.passed,
        }


class ElevationScorer:
    """Computes a weighted composite score from named design signals."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = dict(weights) if weights else dict(DEFAULT_ELEVATION_WEIGHTS)

    def score(self, signals: List[ElevationSignal]) -> ElevationResult:
        signal_map = {s.name: s for s in signals}
        total_weight = sum(self.weights.values())
        breakdown: Dict[str, float] = {}
        hard_fails: List[str] = []
        weighted_sum = 0.0

        for name, weight in self.weights.items():
            signal = signal_map.get(name)
            if signal is None:
                # Missing signal is treated as 0 — an unmeasured dimension
                # must never silently inflate the score. Mirrors the
                # missing-data caution — an unmeasured dimension defaults to failing,
                # never to a free pass.
                signal_score = 0.0
                hard_fails.append(f"missing signal: {name}")
            else:
                signal_score = signal.score
                if signal_score < HARD_FAIL_FLOOR:
                    hard_fails.append(
                        f"{name} below floor ({signal_score:.1f} < {HARD_FAIL_FLOOR})"
                        + (f": {signal.evidence}" if signal.evidence else "")
                    )

            weighted_sum += signal_score * weight
            # Proportional contribution of this dimension to the final
            # total_score, useful for showing *why* a score landed where
            # it did (auditability — see ElevationSignal.evidence).
            breakdown[name] = round(signal_score * (weight / total_weight), 2) if total_weight else 0.0

        total_score = round(weighted_sum / total_weight, 2) if total_weight else 0.0

        return ElevationResult(
            total_score=total_score,
            weighted_breakdown=breakdown,
            hard_fails=hard_fails,
            passed=False,  # GovernanceGate decides pass/fail, not the scorer
        )


class GovernanceGate:
    """The gate a redesign must pass before it can go to the client or
    be committed by Site Builder. See ARCHITECTURE_PRINCIPLES.md §1, §5.

    A redesign must clear BOTH the weighted score threshold AND have no
    individual hard-fail dimension — see ARCHITECTURE_PRINCIPLES.md §5.
    """

    def __init__(
        self,
        scorer: Optional[ElevationScorer] = None,
        threshold: float = 75.0,
        memory: Optional[MemoryStore] = None,
        record_to_memory: bool = True,
    ):
        self.scorer = scorer or ElevationScorer()
        self.threshold = threshold
        # ARCHITECTURE_PRINCIPLES.md §4/§10: every gate evaluation is
        # recorded, not just approvals — a history of blocked attempts is
        # exactly what future scoring recalibration (§6) needs as data.
        self.memory = memory or get_memory_store()
        self.record_to_memory = record_to_memory

    def evaluate(
        self,
        signals: List[ElevationSignal],
        task_id: str = "unknown",
        subject: str = "unknown",
    ) -> ElevationResult:
        result = self.scorer.score(signals)

        blocked_by_hard_fail = len(result.hard_fails) > 0
        blocked_by_score = result.total_score < self.threshold
        result.passed = not blocked_by_hard_fail and not blocked_by_score

        emit_event(
            EventType.GATE_EVALUATED,
            task_id=task_id,
            data={"subject": subject, **result.to_dict(), "threshold": self.threshold},
        )

        if result.passed:
            emit_event(
                EventType.GATE_APPROVED,
                task_id=task_id,
                data={"subject": subject, "total_score": result.total_score},
            )
        else:
            if blocked_by_score:
                emit_event(
                    EventType.SCORE_TOO_LOW,
                    task_id=task_id,
                    data={
                        "subject": subject,
                        "total_score": result.total_score,
                        "threshold": self.threshold,
                    },
                )
            emit_event(
                EventType.GATE_BLOCKED,
                task_id=task_id,
                data={"subject": subject, **result.to_dict()},
            )

        if self.record_to_memory:
            self.memory.remember(
                category=MemoryCategory.GATE_EVALUATION,
                subject=subject,
                content={**result.to_dict(), "threshold": self.threshold},
                tags=["passed"] if result.passed else ["blocked"],
                task_id=task_id,
            )

        return result
