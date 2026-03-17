from __future__ import annotations

import json
from pathlib import Path

from prompt_optimizer.core.improvement_models import ImproveRequest


class InputValidationError(ValueError):
    """Raise when external input cannot be normalized into domain objects."""


def normalize_improve_request_payload(payload: object) -> ImproveRequest:
    """Normalize raw JSON data into an `ImproveRequest`.

    Args:
        payload: Parsed JSON payload expected to contain improve request fields.

    Returns:
        ImproveRequest: The validated and normalized request.

    Raises:
        InputValidationError: If the payload shape or field values are invalid.
    """
    if not isinstance(payload, dict):
        raise InputValidationError("Input must be a valid JSON object.")

    allowed_field_names = {
        "originalPrompt",
        "improvementRequests",
        "ioExamples",
        "additionalConstraints",
        "context",
    }
    unknown_field_names = sorted(set(payload) - allowed_field_names)
    if unknown_field_names:
        unknown_fields = ", ".join(unknown_field_names)
        raise InputValidationError(f"Unknown input fields: {unknown_fields}.")

    original_prompt = _normalize_required_text_field(payload, "originalPrompt")
    improvement_requests = _normalize_optional_text_collection(payload, "improvementRequests")
    io_examples = _normalize_optional_text_collection(payload, "ioExamples")
    additional_constraints = _normalize_optional_text_collection(payload, "additionalConstraints")
    context = _normalize_optional_text_field(payload, "context")

    return ImproveRequest(
        original_prompt=original_prompt,
        improvement_requests=improvement_requests,
        io_examples=io_examples,
        additional_constraints=additional_constraints,
        context=context,
    )


def load_improve_request_from_text(input_text: str) -> ImproveRequest:
    """Parse and normalize an improve request from text.

    Args:
        input_text: Raw JSON text.

    Returns:
        ImproveRequest: The validated request.

    Raises:
        InputValidationError: If the text is empty or does not contain a valid request.
    """
    if not input_text.strip():
        raise InputValidationError("Input must contain a valid JSON object.")

    try:
        payload = json.loads(input_text)
    except json.JSONDecodeError as error:
        raise InputValidationError("Input must be a valid JSON object.") from error

    return normalize_improve_request_payload(payload)


def load_improve_request_from_file(input_file_path: Path) -> ImproveRequest:
    """Load and normalize an improve request from a JSON file.

    Args:
        input_file_path: File path that should contain a JSON request payload.

    Returns:
        ImproveRequest: The validated request.

    Raises:
        InputValidationError: If the file cannot be read or does not contain a valid request.
    """
    try:
        input_text = input_file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputValidationError(f"Unable to read input file: {input_file_path}.") from error

    return load_improve_request_from_text(input_text)


def _normalize_required_text_field(payload: dict[object, object], field_name: str) -> str:
    if field_name not in payload:
        raise InputValidationError(f"{field_name} is required.")

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise InputValidationError(f"{field_name} must be a string.")

    normalized_value = field_value.strip()
    if not normalized_value:
        raise InputValidationError(f"{field_name} must not be empty.")

    return normalized_value


def _normalize_optional_text_field(payload: dict[object, object], field_name: str) -> str | None:
    if field_name not in payload or payload[field_name] is None:
        return None

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise InputValidationError(f"{field_name} must be a string.")

    normalized_value = field_value.strip()
    if not normalized_value:
        raise InputValidationError(f"{field_name} must not be empty when provided.")

    return normalized_value


def _normalize_optional_text_collection(
    payload: dict[object, object], field_name: str
) -> tuple[str, ...]:
    if field_name not in payload or payload[field_name] is None:
        return ()

    field_value = payload[field_name]
    if isinstance(field_value, str):
        return (_normalize_collection_item(field_value, field_name),)

    if isinstance(field_value, list):
        normalized_values: list[str] = []
        for item in field_value:
            if not isinstance(item, str):
                raise InputValidationError(f"{field_name} must contain only strings.")
            normalized_values.append(_normalize_collection_item(item, field_name))
        return tuple(normalized_values)

    raise InputValidationError(f"{field_name} must be a string or a list of strings.")


def _normalize_collection_item(field_value: str, field_name: str) -> str:
    normalized_value = field_value.strip()
    if not normalized_value:
        raise InputValidationError(f"{field_name} must not contain empty values.")

    return normalized_value
