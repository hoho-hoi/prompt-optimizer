from __future__ import annotations

from prompt_optimizer.core.improvement_models import (
    DomainValidationError,
    ImproveResult,
    Judgment,
)
from prompt_optimizer.core.structured_response_models import StructuredImproveResponse


class ResponseValidationError(ValueError):
    """Raise when model output cannot be normalized into the response contract."""


def parse_structured_improve_response(payload: object, *, original_prompt: str) -> ImproveResult:
    """Parse and validate a structured LLM improve response.

    Args:
        payload: Parsed response payload expected from the LLM output.
        original_prompt: Original prompt used to validate consistency rules.

    Returns:
        ImproveResult: Validated improvement result.

    Raises:
        ResponseValidationError: If the payload shape or values are invalid.
    """
    structured_response = normalize_structured_improve_response_payload(payload)

    try:
        return structured_response.to_improve_result(original_prompt=original_prompt)
    except DomainValidationError as error:
        raise ResponseValidationError(str(error)) from error


def normalize_structured_improve_response_payload(payload: object) -> StructuredImproveResponse:
    """Normalize raw payload into a structured response contract.

    Args:
        payload: Parsed response payload expected to contain contract fields.

    Returns:
        StructuredImproveResponse: Validated structured response.

    Raises:
        ResponseValidationError: If the payload shape or field values are invalid.
    """
    if not isinstance(payload, dict):
        raise ResponseValidationError("Response must be a valid JSON object.")

    allowed_field_names = {"judgment", "reason", "improvedPrompt", "changes"}
    unknown_field_names = sorted(set(payload) - allowed_field_names)
    if unknown_field_names:
        unknown_fields = ", ".join(unknown_field_names)
        raise ResponseValidationError(f"Unknown response fields: {unknown_fields}.")

    judgment = _normalize_judgment_field(payload)
    reason = _normalize_required_text_field(payload, "reason")
    improved_prompt = _normalize_required_text_field(payload, "improvedPrompt")
    changes = _normalize_changes_field(payload)

    return StructuredImproveResponse(
        judgment=judgment,
        reason=reason,
        improved_prompt=improved_prompt,
        changes=changes,
    )


def _normalize_judgment_field(payload: dict[object, object]) -> Judgment:
    if "judgment" not in payload:
        raise ResponseValidationError("judgment is required.")

    raw_judgment = payload["judgment"]
    if not isinstance(raw_judgment, str):
        raise ResponseValidationError("judgment must be a string.")

    normalized_judgment = raw_judgment.strip()
    if not normalized_judgment:
        raise ResponseValidationError("judgment must not be empty.")

    try:
        return Judgment(normalized_judgment)
    except ValueError as error:
        allowed_judgments = ", ".join(judgment.value for judgment in Judgment)
        raise ResponseValidationError(f"judgment must be one of: {allowed_judgments}.") from error


def _normalize_required_text_field(payload: dict[object, object], field_name: str) -> str:
    if field_name not in payload:
        raise ResponseValidationError(f"{field_name} is required.")

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise ResponseValidationError(f"{field_name} must be a string.")

    normalized_value = field_value.strip()
    if not normalized_value:
        raise ResponseValidationError(f"{field_name} must not be empty.")

    return normalized_value


def _normalize_changes_field(payload: dict[object, object]) -> tuple[str, ...]:
    if "changes" not in payload:
        raise ResponseValidationError("changes is required.")

    field_value = payload["changes"]
    if not isinstance(field_value, list):
        raise ResponseValidationError("changes must be a list of strings.")

    normalized_changes: list[str] = []
    for item in field_value:
        if not isinstance(item, str):
            raise ResponseValidationError("changes must contain only strings.")

        normalized_item = item.strip()
        if not normalized_item:
            raise ResponseValidationError("changes must not contain empty values.")
        normalized_changes.append(normalized_item)

    return tuple(normalized_changes)
