from __future__ import annotations

from dataclasses import dataclass

from prompt_optimizer.core.improvement_models import ImproveResult, Judgment


@dataclass(frozen=True, slots=True, kw_only=True)
class StructuredImproveResponse:
    """Represent the structured LLM response contract for prompt improvement.

    Attributes:
        judgment: Improvement decision returned by the model.
        reason: Human-readable explanation for the decision.
        improved_prompt: Resulting prompt text returned by the model.
        changes: Structured summary of the modifications made by the model.
    """

    judgment: Judgment
    reason: str
    improved_prompt: str
    changes: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        """Serialize the response using the public contract field names.

        Returns:
            dict[str, object]: A JSON-serializable structured response payload.
        """
        return {
            "judgment": self.judgment.value,
            "reason": self.reason,
            "improvedPrompt": self.improved_prompt,
            "changes": list(self.changes),
        }

    def to_improve_result(self, *, original_prompt: str) -> ImproveResult:
        """Convert the structured response into the validated domain result.

        Args:
            original_prompt: Original prompt used to validate cross-field invariants.

        Returns:
            ImproveResult: Domain result with existing invariant checks applied.
        """
        return ImproveResult(
            judgment=self.judgment,
            reason=self.reason,
            improved_prompt=self.improved_prompt,
            changes=self.changes,
            original_prompt=original_prompt,
        )
