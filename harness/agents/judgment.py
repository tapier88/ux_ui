"""
Provider-agnostic design judgment engine.

This module generalizes the Qwen adapter pattern for creative/design judgment
work. Skills can depend on this stable engine contract while swapping the
underlying LLM provider between mock, Qwen, or any future provider that
implements `LLMProvider`.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from harness.agents import LLMProvider, LLMRequest, LLMResponse, get_default_provider


@dataclass
class DesignJudgmentRequest:
    """Structured input for a design judgment."""

    judgment_type: str
    subject: str
    context: Dict[str, Any] = field(default_factory=dict)
    criteria: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DesignJudgmentResult:
    """Provider-normalized output for a design judgment."""

    decision: str
    rationale: str
    confidence: float
    provider_status: str
    raw_response: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "provider_status": self.provider_status,
            "raw_response": self.raw_response,
            "metadata": self.metadata,
        }


class BaseDesignJudgmentEngine:
    """
    Base engine for design/creative judgments.

    Subclasses may override `build_prompt` and `parse_response`; the public
    `judge` contract stays provider-agnostic.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are evaluating design work. Return a clear decision, concise "
        "rationale, and confidence based only on the provided context."
    )

    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        self.provider = provider or get_default_provider()
        self.system_prompt = system_prompt

    def judge(self, request: DesignJudgmentRequest) -> DesignJudgmentResult:
        """Run one judgment through the configured provider."""
        self._validate_request(request)
        prompt = self.build_prompt(request)
        response = self.provider.generate(
            LLMRequest(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.2,
                metadata={
                    "judgment_type": request.judgment_type,
                    **request.metadata,
                },
            )
        )
        return self.parse_response(request, response)

    def build_prompt(self, request: DesignJudgmentRequest) -> str:
        """Build a deterministic prompt from structured judgment inputs."""
        criteria = request.criteria or ["overall design quality"]
        context_lines = [
            f"- {key}: {value}" for key, value in sorted(request.context.items())
        ]
        criteria_lines = [f"- {criterion}" for criterion in criteria]

        return "\n".join(
            [
                f"Judgment type: {request.judgment_type}",
                f"Subject: {request.subject}",
                "Criteria:",
                *criteria_lines,
                "Context:",
                *(context_lines or ["- none"]),
                "Required response: decision, rationale, confidence.",
            ]
        )

    def parse_response(
        self,
        request: DesignJudgmentRequest,
        response: LLMResponse,
    ) -> DesignJudgmentResult:
        """
        Convert provider output into a stable result.

        The default parser is intentionally conservative. Provider-specific
        subclasses can parse structured JSON or richer schemas later.
        """
        raw = response.content.strip()
        lowered = raw.lower()
        decision = "review"
        confidence = 0.5

        if any(token in lowered for token in ("approve", "approved", "pass", "ready")):
            decision = "approve"
            confidence = 0.7
        elif any(token in lowered for token in ("reject", "blocked", "block", "fail")):
            decision = "reject"
            confidence = 0.7

        return DesignJudgmentResult(
            decision=decision,
            rationale=raw,
            confidence=confidence,
            provider_status=self.provider.get_status().value,
            raw_response=response.content,
            metadata={
                "judgment_type": request.judgment_type,
                **request.metadata,
                "provider_metadata": response.metadata,
            },
        )

    def _validate_request(self, request: DesignJudgmentRequest):
        if not request.judgment_type.strip():
            raise ValueError("judgment_type is required")
        if not request.subject.strip():
            raise ValueError("subject is required")
