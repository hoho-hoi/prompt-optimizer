from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class DomainValidationError(ValueError):
    """Raise when a domain object violates required invariants."""


class Judgment(StrEnum):
    """Represent the decision for whether a prompt should be improved."""

    NO_IMPROVEMENT_NEEDED = "改善不要"
    IMPROVEMENT_RECOMMENDED = "改善推奨"
    IMPROVEMENT_REQUIRED = "改善必須"


@dataclass(frozen=True, slots=True, kw_only=True)
class ImproveRequest:
    """Represent normalized input for a prompt improvement operation.

    Attributes:
        request_id: Stable session-scoped identifier for the request.
        original_prompt: The original prompt text that must be evaluated.
        improvement_requests: Optional user requests that guide evaluation.
        io_examples: Optional examples that provide desired input/output behavior.
        additional_constraints: Optional constraints that the result should respect.
        context: Optional background information for the request.
    """

    request_id: str = field(default_factory=lambda: str(uuid4()))
    original_prompt: str
    improvement_requests: tuple[str, ...] = ()
    io_examples: tuple[str, ...] = ()
    additional_constraints: tuple[str, ...] = ()
    context: str | None = None

    def __post_init__(self) -> None:
        """Validate the request after construction."""
        _require_non_empty_text(self.request_id, "request_id")
        _require_non_empty_text(self.original_prompt, "original_prompt")
        _validate_text_items(self.improvement_requests, "improvement_requests")
        _validate_text_items(self.io_examples, "io_examples")
        _validate_text_items(self.additional_constraints, "additional_constraints")
        if self.context is not None:
            _require_non_empty_text(self.context, "context")

    def to_payload(self) -> dict[str, object]:
        """Serialize the request using the public JSON field names.

        Returns:
            dict[str, object]: A JSON-serializable representation of the request.
        """
        return {
            "requestId": self.request_id,
            "originalPrompt": self.original_prompt,
            "improvementRequests": list(self.improvement_requests),
            "ioExamples": list(self.io_examples),
            "additionalConstraints": list(self.additional_constraints),
            "context": self.context,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ImproveResult:
    """Represent the evaluated result of a prompt improvement operation.

    Attributes:
        result_id: Stable persisted identifier for the improvement result.
        judgment: The domain judgment for the original prompt.
        reason: Human-readable reasoning for the judgment.
        improved_prompt: The resulting prompt text after evaluation.
        changes: Structured descriptions of the changes that were applied.
        original_prompt: The original input prompt used for invariant validation.
    """

    result_id: str = field(default_factory=lambda: str(uuid4()))
    judgment: Judgment
    reason: str
    improved_prompt: str
    changes: tuple[str, ...]
    original_prompt: str

    def __post_init__(self) -> None:
        """Validate cross-field invariants for the result."""
        _require_non_empty_text(self.result_id, "result_id")
        _require_non_empty_text(self.reason, "reason")
        _require_non_empty_text(self.improved_prompt, "improved_prompt")
        _require_non_empty_text(self.original_prompt, "original_prompt")
        _validate_text_items(self.changes, "changes")

        if self.judgment is Judgment.NO_IMPROVEMENT_NEEDED:
            if self.improved_prompt != self.original_prompt:
                raise DomainValidationError(
                    "ImproveResult with judgment='改善不要' must keep the original prompt."
                )
            if self.changes:
                raise DomainValidationError(
                    "ImproveResult with judgment='改善不要' must not contain changes."
                )

    @property
    def changes_summary(self) -> str:
        """Return the user-facing summary for changes.

        Returns:
            str: `"なし"` when there are no changes, otherwise a joined summary.
        """
        if not self.changes:
            return "なし"

        return "\n".join(self.changes)

    def to_payload(self) -> dict[str, str]:
        """Serialize the result using the public JSON field names.

        Returns:
            dict[str, str]: A JSON-serializable representation of the result.
        """
        return {
            "resultId": self.result_id,
            "judgment": self.judgment.value,
            "reason": self.reason,
            "improvedPrompt": self.improved_prompt,
            "changes": self.changes_summary,
        }


def _require_non_empty_text(value: str, field_name: str) -> None:
    stripped_value = value.strip()
    if not stripped_value:
        raise DomainValidationError(f"{field_name} must not be empty.")


def _validate_text_items(values: tuple[str, ...], field_name: str) -> None:
    for value in values:
        _require_non_empty_text(value, field_name)
