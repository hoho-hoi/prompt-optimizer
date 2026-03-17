import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from prompt_optimizer.cli.main import application_cli
from prompt_optimizer.core import (
    DomainValidationError,
    ImproveRequest,
    ImproveResult,
    InputValidationError,
    Judgment,
    load_improve_request_from_file,
    load_improve_request_from_text,
    normalize_improve_request_payload,
)


def test_normalize_improve_request_with_required_field_only() -> None:
    normalized_request = normalize_improve_request_payload(
        {
            "originalPrompt": "  Draft a release note.  ",
        }
    )

    assert normalized_request.original_prompt == "Draft a release note."
    assert normalized_request.improvement_requests == ()
    assert normalized_request.io_examples == ()
    assert normalized_request.additional_constraints == ()
    assert normalized_request.context is None
    assert normalized_request.request_id


def test_normalize_improve_request_with_optional_fields() -> None:
    normalized_request = normalize_improve_request_payload(
        {
            "originalPrompt": "Summarize the changelog.",
            "improvementRequests": [
                "Make the output concise.",
                "Keep the tone professional.",
            ],
            "ioExamples": "Input: changelog\nOutput: summary",
            "additionalConstraints": ["Avoid bullet points."],
            "context": "Release management workflow",
        }
    )

    assert normalized_request.original_prompt == "Summarize the changelog."
    assert normalized_request.improvement_requests == (
        "Make the output concise.",
        "Keep the tone professional.",
    )
    assert normalized_request.io_examples == ("Input: changelog\nOutput: summary",)
    assert normalized_request.additional_constraints == ("Avoid bullet points.",)
    assert normalized_request.context == "Release management workflow"
    assert normalized_request.request_id


def test_improve_request_generates_identifier_and_serializes_it() -> None:
    improve_request = ImproveRequest(original_prompt="Review this prompt.")

    payload = improve_request.to_payload()

    assert improve_request.request_id
    assert payload["requestId"] == improve_request.request_id
    assert payload["originalPrompt"] == "Review this prompt."


def test_improve_request_preserves_explicit_identifier() -> None:
    improve_request = ImproveRequest(
        request_id="request-session-001",
        original_prompt="Review this prompt.",
    )

    assert improve_request.request_id == "request-session-001"


def test_normalize_improve_request_rejects_missing_original_prompt() -> None:
    with pytest.raises(InputValidationError, match="originalPrompt is required"):
        normalize_improve_request_payload({})


def test_load_improve_request_from_file_reads_json_payload(
    tmp_path: Path,
) -> None:
    input_file_path = tmp_path / "request.json"
    input_file_path.write_text(
        json.dumps(
            {
                "originalPrompt": "Improve this prompt.",
                "context": "Internal support workflow",
            }
        ),
        encoding="utf-8",
    )

    normalized_request = load_improve_request_from_file(input_file_path)

    assert normalized_request.original_prompt == "Improve this prompt."
    assert normalized_request.context == "Internal support workflow"


def test_load_improve_request_from_text_rejects_invalid_json() -> None:
    with pytest.raises(InputValidationError, match="valid JSON object"):
        load_improve_request_from_text("not-json")


def test_improve_result_rejects_inconsistent_no_change_result() -> None:
    with pytest.raises(DomainValidationError, match="must keep the original prompt"):
        ImproveResult(
            judgment=Judgment.NO_IMPROVEMENT_NEEDED,
            reason="The prompt is already clear.",
            improved_prompt="Edited prompt.",
            changes=("Shortened wording.",),
            original_prompt="Original prompt.",
        )


def test_improve_result_accepts_consistent_no_change_result() -> None:
    improve_result = ImproveResult(
        judgment=Judgment.NO_IMPROVEMENT_NEEDED,
        reason="The prompt is already clear.",
        improved_prompt="Original prompt.",
        changes=(),
        original_prompt="Original prompt.",
    )

    assert improve_result.changes_summary == "なし"


def test_improve_result_generates_identifier_and_serializes_it() -> None:
    improve_result = ImproveResult(
        judgment=Judgment.IMPROVEMENT_RECOMMENDED,
        reason="The prompt needs clearer success criteria.",
        improved_prompt="Add success criteria to the prompt.",
        changes=("Added explicit success criteria.",),
        original_prompt="Write a better prompt.",
    )

    payload = improve_result.to_payload()

    assert improve_result.result_id
    assert payload["resultId"] == improve_result.result_id
    assert payload["changes"] == "Added explicit success criteria."


def test_improve_result_preserves_explicit_identifier() -> None:
    improve_result = ImproveResult(
        result_id="result-persisted-001",
        judgment=Judgment.IMPROVEMENT_RECOMMENDED,
        reason="The prompt needs clearer success criteria.",
        improved_prompt="Add success criteria to the prompt.",
        changes=("Added explicit success criteria.",),
        original_prompt="Write a better prompt.",
    )

    assert improve_result.result_id == "result-persisted-001"


def test_improve_command_reads_payload_from_input_file(tmp_path: Path) -> None:
    input_file_path = tmp_path / "request.json"
    input_file_path.write_text(
        json.dumps(
            {
                "originalPrompt": "Explain the deployment process.",
                "additionalConstraints": ["Use plain language."],
            }
        ),
        encoding="utf-8",
    )
    cli_runner = CliRunner()

    result = cli_runner.invoke(application_cli, ["improve", "--input", str(input_file_path)])

    assert result.exit_code == 0
    response_payload = json.loads(result.stdout)
    assert response_payload["request"]["requestId"]
    assert response_payload["request"]["originalPrompt"] == "Explain the deployment process."
    assert response_payload["request"]["additionalConstraints"] == ["Use plain language."]


def test_improve_command_reads_payload_from_standard_input() -> None:
    cli_runner = CliRunner()

    result = cli_runner.invoke(
        application_cli,
        ["improve"],
        input=json.dumps(
            {
                "originalPrompt": "Generate a retrospective summary.",
                "improvementRequests": ["Reduce repetition."],
            }
        ),
    )

    assert result.exit_code == 0
    response_payload = json.loads(result.stdout)
    assert response_payload["request"]["requestId"]
    assert response_payload["request"]["originalPrompt"] == "Generate a retrospective summary."
    assert response_payload["request"]["improvementRequests"] == ["Reduce repetition."]


def test_improve_command_rejects_invalid_input_file_payload(tmp_path: Path) -> None:
    input_file_path = tmp_path / "request.json"
    input_file_path.write_text('{"context": "missing"}', encoding="utf-8")
    cli_runner = CliRunner()

    result = cli_runner.invoke(application_cli, ["improve", "--input", str(input_file_path)])

    assert result.exit_code == 1
    assert "originalPrompt is required" in result.output


def test_improve_command_rejects_invalid_standard_input_payload() -> None:
    cli_runner = CliRunner()

    result = cli_runner.invoke(application_cli, ["improve"], input="{")

    assert result.exit_code == 1
    assert "valid JSON object" in result.output
