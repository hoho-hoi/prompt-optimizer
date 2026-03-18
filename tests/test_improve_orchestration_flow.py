from prompt_optimizer.core import (
    ExecutionConfiguration,
    ImproveRequest,
    Judgment,
    OutputFormat,
    PromptModule,
    PromptModuleType,
    RenderedPrompt,
    StructuredImproveResponse,
)
from prompt_optimizer.core.improve_orchestrator import ImprovePromptService


class RecordingModelGateway:
    def __init__(self, *, structured_response: StructuredImproveResponse) -> None:
        self.structured_response = structured_response
        self.recorded_prompt: RenderedPrompt | None = None
        self.recorded_configuration: ExecutionConfiguration | None = None

    def generate_structured_improve_response(
        self,
        *,
        rendered_prompt: RenderedPrompt,
        execution_configuration: ExecutionConfiguration,
    ) -> StructuredImproveResponse:
        self.recorded_prompt = rendered_prompt
        self.recorded_configuration = execution_configuration
        return self.structured_response


def test_improve_prompt_service_orchestrates_render_call_and_result_conversion() -> None:
    model_gateway = RecordingModelGateway(
        structured_response=StructuredImproveResponse(
            judgment=Judgment.IMPROVEMENT_RECOMMENDED,
            reason="The prompt does not define the response format clearly.",
            improved_prompt="Summarize the changelog in three concise bullet points.",
            changes=(
                "Added an explicit output format.",
                "Constrained the response length.",
            ),
        )
    )
    improve_service = ImprovePromptService(
        prompt_module=PromptModule(
            module_id="module-improve-default",
            module_type=PromptModuleType.EVALUATION,
            prompt_body="Evaluate the prompt and return JSON only.",
        ),
        model_gateway=model_gateway,
        execution_configuration=ExecutionConfiguration(
            model_name="gpt-4.1-mini",
            allow_no_change=True,
            strict_minimal_edit=True,
            prefer_short=True,
            output_format=OutputFormat.JSON,
        ),
    )

    improve_result = improve_service.execute_improve_request(
        ImproveRequest(
            original_prompt="Summarize the changelog.",
            improvement_requests=("Keep the result concise.",),
            context="Release communication workflow",
        )
    )

    assert improve_result.judgment is Judgment.IMPROVEMENT_RECOMMENDED
    assert (
        improve_result.improved_prompt == "Summarize the changelog in three concise bullet points."
    )
    assert improve_result.changes == (
        "Added an explicit output format.",
        "Constrained the response length.",
    )
    assert model_gateway.recorded_prompt is not None
    assert "Original Prompt:\nSummarize the changelog." in model_gateway.recorded_prompt.prompt_text
    assert (
        "Improvement Requests:\n- Keep the result concise."
        in model_gateway.recorded_prompt.prompt_text
    )
    assert "Context:\nRelease communication workflow" in model_gateway.recorded_prompt.prompt_text
    assert model_gateway.recorded_configuration is not None
    assert model_gateway.recorded_configuration.model_name == "gpt-4.1-mini"


def test_improve_prompt_service_preserves_no_change_invariants() -> None:
    model_gateway = RecordingModelGateway(
        structured_response=StructuredImproveResponse(
            judgment=Judgment.NO_IMPROVEMENT_NEEDED,
            reason="The prompt already matches the requested behavior.",
            improved_prompt="Generate a retrospective summary.",
            changes=(),
        )
    )
    improve_service = ImprovePromptService(
        prompt_module=PromptModule(
            module_id="module-improve-default",
            module_type=PromptModuleType.EVALUATION,
            prompt_body="Evaluate the prompt and return JSON only.",
        ),
        model_gateway=model_gateway,
        execution_configuration=ExecutionConfiguration(model_name="gpt-4.1-mini"),
    )

    improve_result = improve_service.execute_improve_request(
        ImproveRequest(original_prompt="Generate a retrospective summary.")
    )

    assert improve_result.judgment is Judgment.NO_IMPROVEMENT_NEEDED
    assert improve_result.improved_prompt == "Generate a retrospective summary."
    assert improve_result.changes_summary == "なし"
