import pytest

from prompt_optimizer.core import ImproveRequest
from prompt_optimizer.core.llm_response_parser import (
    ResponseValidationError,
    parse_structured_improve_response,
)
from prompt_optimizer.core.prompt_module_models import (
    PromptModule,
    PromptModuleType,
    RenderedPrompt,
)


def test_render_prompt_module_builds_rendered_prompt_with_request_context() -> None:
    prompt_module = PromptModule(
        module_id="module-evaluation-default",
        module_type=PromptModuleType.EVALUATION,
        prompt_body="Evaluate the prompt and respond with structured JSON.",
    )
    improve_request = ImproveRequest(
        original_prompt="Summarize release notes for executives.",
        improvement_requests=("Keep the result concise.",),
        io_examples=("Input: release note\nOutput: concise summary",),
        additional_constraints=("Avoid bullet points.",),
        context="The audience is leadership.",
    )

    rendered_prompt = prompt_module.render_prompt(improve_request)

    assert rendered_prompt == RenderedPrompt(
        module_id="module-evaluation-default",
        module_type=PromptModuleType.EVALUATION,
        prompt_text=(
            "Evaluate the prompt and respond with structured JSON.\n\n"
            "Original Prompt:\n"
            "Summarize release notes for executives.\n\n"
            "Improvement Requests:\n"
            "- Keep the result concise.\n\n"
            "Input/Output Examples:\n"
            "- Input: release note\nOutput: concise summary\n\n"
            "Additional Constraints:\n"
            "- Avoid bullet points.\n\n"
            "Context:\n"
            "The audience is leadership."
        ),
    )


def test_prompt_module_rejects_empty_prompt_body() -> None:
    with pytest.raises(ValueError, match="prompt_body must not be empty"):
        PromptModule(
            module_id="module-evaluation-default",
            module_type=PromptModuleType.EVALUATION,
            prompt_body="   ",
        )


def test_parse_structured_improve_response_returns_improve_result() -> None:
    improve_result = parse_structured_improve_response(
        {
            "judgment": "改善推奨",
            "reason": "The original prompt lacks explicit output constraints.",
            "improvedPrompt": "Summarize release notes in three short sentences.",
            "changes": [
                "Added an explicit sentence limit.",
                "Clarified the expected output shape.",
            ],
        },
        original_prompt="Summarize release notes.",
    )

    assert improve_result.judgment.value == "改善推奨"
    assert improve_result.reason == "The original prompt lacks explicit output constraints."
    assert improve_result.improved_prompt == "Summarize release notes in three short sentences."
    assert improve_result.changes == (
        "Added an explicit sentence limit.",
        "Clarified the expected output shape.",
    )
    assert improve_result.original_prompt == "Summarize release notes."


def test_parse_structured_improve_response_rejects_invalid_judgment() -> None:
    with pytest.raises(ResponseValidationError, match="judgment must be one of"):
        parse_structured_improve_response(
            {
                "judgment": "未定",
                "reason": "The model could not determine the result.",
                "improvedPrompt": "Summarize release notes.",
                "changes": [],
            },
            original_prompt="Summarize release notes.",
        )


def test_parse_structured_improve_response_rejects_empty_reason() -> None:
    with pytest.raises(ResponseValidationError, match="reason must not be empty"):
        parse_structured_improve_response(
            {
                "judgment": "改善推奨",
                "reason": "   ",
                "improvedPrompt": "Summarize release notes in three short sentences.",
                "changes": ["Added a sentence limit."],
            },
            original_prompt="Summarize release notes.",
        )


def test_parse_structured_improve_response_rejects_inconsistent_no_improvement_payload() -> None:
    with pytest.raises(ResponseValidationError, match="must keep the original prompt"):
        parse_structured_improve_response(
            {
                "judgment": "改善不要",
                "reason": "The original prompt already meets the goal.",
                "improvedPrompt": "Summarize release notes in three short sentences.",
                "changes": ["Changed the response format."],
            },
            original_prompt="Summarize release notes.",
        )
