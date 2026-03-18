from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from prompt_optimizer.core.configuration_loader import load_model_api_configuration
from prompt_optimizer.core.configuration_models import (
    ApplicationSetting,
    ExecutionConfiguration,
    OutputFormat,
)
from prompt_optimizer.core.improvement_models import (
    DomainValidationError,
    ImproveRequest,
    ImproveResult,
)
from prompt_optimizer.core.llm_response_parser import ResponseValidationError
from prompt_optimizer.core.model_gateway import ModelGateway, OpenAiCompatibleModelGateway
from prompt_optimizer.core.prompt_module_models import PromptModule, PromptModuleType

DEFAULT_MODEL_NAME = "gpt-4.1-mini"
DEFAULT_PROMPT_BODY = """
You improve prompts for maintainability, clarity, and minimal edits.
First evaluate whether the original prompt already meets its goal.
If improvement is needed, preserve the original intent and apply only the minimum necessary edits.
Return JSON only.
""".strip()


class ImprovePromptUseCase(Protocol):
    """Represent the public interface for prompt improvement orchestration."""

    def execute_improve_request(self, improve_request: ImproveRequest) -> ImproveResult:
        """Execute the improve flow for a normalized improve request."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ImprovePromptService:
    """Coordinate prompt rendering, model execution, and result validation.

    Attributes:
        prompt_module: Prompt template used to render the model input.
        model_gateway: Gateway responsible for the structured model call.
        execution_configuration: Runtime options for the model execution.
    """

    prompt_module: PromptModule
    model_gateway: ModelGateway
    execution_configuration: ExecutionConfiguration

    def execute_improve_request(self, improve_request: ImproveRequest) -> ImproveResult:
        """Execute the improve flow for a normalized request.

        Args:
            improve_request: Validated improve request payload.

        Returns:
            ImproveResult: Validated user-facing improvement result.

        Raises:
            ResponseValidationError: If the model response violates result invariants.
        """
        rendered_prompt = self.prompt_module.render_prompt(improve_request)
        structured_response = self.model_gateway.generate_structured_improve_response(
            rendered_prompt=rendered_prompt,
            execution_configuration=self.execution_configuration,
        )

        try:
            return structured_response.to_improve_result(
                original_prompt=improve_request.original_prompt
            )
        except DomainValidationError as error:
            raise ResponseValidationError(str(error)) from error


def create_default_improve_service(
    *, environment_variables: Mapping[str, str] | None = None
) -> ImprovePromptUseCase:
    """Create the default improve service used by the CLI.

    Args:
        environment_variables: Optional environment mapping for configuration resolution.

    Returns:
        ImprovePromptUseCase: Fully wired prompt improvement service.
    """
    resolved_environment_variables: Mapping[str, str]
    if environment_variables is None:
        resolved_environment_variables = os.environ
    else:
        resolved_environment_variables = environment_variables

    application_setting = ApplicationSetting(
        output_language="Japanese",
        conciseness_priority="high",
        minimal_edit_strength="strict",
        api_setting_ref="env:OPENAI_COMPATIBLE",
    )
    model_api_configuration = load_model_api_configuration(
        application_setting=application_setting,
        environment_variables=resolved_environment_variables,
    )

    return ImprovePromptService(
        prompt_module=PromptModule(
            module_id="module-improve-default",
            module_type=PromptModuleType.EVALUATION,
            prompt_body=DEFAULT_PROMPT_BODY,
        ),
        model_gateway=OpenAiCompatibleModelGateway(
            base_url=model_api_configuration.base_url,
            api_key=model_api_configuration.api_key,
        ),
        execution_configuration=ExecutionConfiguration(
            model_name=_resolve_model_name(environment_variables=resolved_environment_variables),
            allow_no_change=True,
            strict_minimal_edit=True,
            prefer_short=True,
            output_format=OutputFormat.JSON,
        ),
    )


def _resolve_model_name(*, environment_variables: Mapping[str, str]) -> str:
    configured_model_name = environment_variables.get("PROMPT_IMPROVER_MODEL_NAME")
    if configured_model_name is None:
        return DEFAULT_MODEL_NAME

    normalized_model_name = configured_model_name.strip()
    if not normalized_model_name:
        return DEFAULT_MODEL_NAME

    return normalized_model_name
