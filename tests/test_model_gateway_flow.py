import json
from pathlib import Path

import pytest

from prompt_optimizer.core import (
    ApplicationSetting,
    ExecutionConfiguration,
    ModelAuthenticationError,
    ModelConnectionError,
    ModelGatewayResponseError,
    ModelHttpRequest,
    ModelHttpResponse,
    OpenAiCompatibleModelGateway,
    OutputFormat,
    PromptModuleType,
    RenderedPrompt,
    TransportConnectionError,
    load_application_setting_from_file,
    load_model_api_configuration,
    normalize_execution_configuration_payload,
)


def test_normalize_execution_configuration_with_all_supported_fields() -> None:
    execution_configuration = normalize_execution_configuration_payload(
        {
            "modelName": "gpt-4.1-mini",
            "allowNoChange": True,
            "strictMinimalEdit": True,
            "preferShort": False,
            "outputFormat": "json",
        }
    )

    assert execution_configuration.configuration_id
    assert execution_configuration.model_name == "gpt-4.1-mini"
    assert execution_configuration.allow_no_change is True
    assert execution_configuration.strict_minimal_edit is True
    assert execution_configuration.prefer_short is False
    assert execution_configuration.output_format is OutputFormat.JSON


def test_load_application_setting_from_file_preserves_api_setting_reference(
    tmp_path: Path,
) -> None:
    application_setting_file_path = tmp_path / "application-setting.json"
    application_setting_file_path.write_text(
        json.dumps(
            {
                "outputLanguage": "Japanese",
                "concisenessPriority": "high",
                "minimalEditStrength": "strict",
                "apiSettingRef": "env:OPENAI_COMPATIBLE",
            }
        ),
        encoding="utf-8",
    )

    application_setting = load_application_setting_from_file(application_setting_file_path)

    assert application_setting.setting_id
    assert application_setting.output_language == "Japanese"
    assert application_setting.conciseness_priority == "high"
    assert application_setting.minimal_edit_strength == "strict"
    assert application_setting.api_setting_ref == "env:OPENAI_COMPATIBLE"


def test_load_model_api_configuration_from_environment_reference() -> None:
    application_setting = ApplicationSetting(
        output_language="Japanese",
        conciseness_priority="high",
        minimal_edit_strength="strict",
        api_setting_ref="env:OPENAI_COMPATIBLE",
    )

    model_api_configuration = load_model_api_configuration(
        application_setting=application_setting,
        environment_variables={
            "OPENAI_COMPATIBLE_BASE_URL": "https://example.invalid/v1",
            "OPENAI_COMPATIBLE_API_KEY": "test-api-key",
        },
    )

    assert model_api_configuration.base_url == "https://example.invalid/v1"
    assert model_api_configuration.api_key == "test-api-key"


def test_load_model_api_configuration_from_local_reference(tmp_path: Path) -> None:
    local_api_setting_file_path = tmp_path / "local-api-setting.json"
    local_api_setting_file_path.write_text(
        json.dumps(
            {
                "baseUrl": "https://local.invalid/v1",
                "apiKey": "local-test-api-key",
            }
        ),
        encoding="utf-8",
    )
    application_setting = ApplicationSetting(
        output_language="Japanese",
        conciseness_priority="high",
        minimal_edit_strength="strict",
        api_setting_ref=f"local:{local_api_setting_file_path}",
    )

    model_api_configuration = load_model_api_configuration(
        application_setting=application_setting,
        environment_variables={},
    )

    assert model_api_configuration.base_url == "https://local.invalid/v1"
    assert model_api_configuration.api_key == "local-test-api-key"


def test_load_model_api_configuration_rejects_missing_environment_secret() -> None:
    application_setting = ApplicationSetting(
        output_language="Japanese",
        conciseness_priority="high",
        minimal_edit_strength="strict",
        api_setting_ref="env:OPENAI_COMPATIBLE",
    )

    with pytest.raises(ValueError, match="OPENAI_COMPATIBLE_API_KEY is required"):
        load_model_api_configuration(
            application_setting=application_setting,
            environment_variables={"OPENAI_COMPATIBLE_BASE_URL": "https://example.invalid/v1"},
        )


def test_openai_compatible_model_gateway_returns_structured_response() -> None:
    transport = RecordingTransport(
        response=ModelHttpResponse(
            status_code=200,
            body={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "judgment": "改善推奨",
                                    "reason": "The prompt needs clearer output constraints.",
                                    "improvedPrompt": "Summarize the changelog in three sentences.",
                                    "changes": ["Added an explicit sentence limit."],
                                }
                            )
                        }
                    }
                ]
            },
        )
    )
    model_gateway = OpenAiCompatibleModelGateway(
        base_url="https://example.invalid/v1",
        api_key="test-api-key",
        transport=transport,
    )

    structured_response = model_gateway.generate_structured_improve_response(
        rendered_prompt=RenderedPrompt(
            module_id="module-evaluation-default",
            module_type=PromptModuleType.EVALUATION,
            prompt_text="Evaluate the prompt and return JSON only.",
        ),
        execution_configuration=ExecutionConfiguration(
            model_name="gpt-4.1-mini",
            allow_no_change=True,
            strict_minimal_edit=True,
            prefer_short=True,
            output_format=OutputFormat.JSON,
        ),
    )

    assert structured_response.judgment.value == "改善推奨"
    assert structured_response.improved_prompt == "Summarize the changelog in three sentences."
    assert transport.recorded_request is not None
    assert transport.recorded_request.url == "https://example.invalid/v1/chat/completions"
    assert transport.recorded_request.headers["Authorization"] == "Bearer test-api-key"
    assert transport.recorded_request.body["model"] == "gpt-4.1-mini"


def test_openai_compatible_model_gateway_maps_authentication_failure() -> None:
    transport = RecordingTransport(response=ModelHttpResponse(status_code=401, body={"error": {}}))
    model_gateway = OpenAiCompatibleModelGateway(
        base_url="https://example.invalid/v1",
        api_key="test-api-key",
        transport=transport,
    )

    with pytest.raises(ModelAuthenticationError, match="Authentication failed"):
        model_gateway.generate_structured_improve_response(
            rendered_prompt=RenderedPrompt(
                module_id="module-evaluation-default",
                module_type=PromptModuleType.EVALUATION,
                prompt_text="Evaluate the prompt and return JSON only.",
            ),
            execution_configuration=ExecutionConfiguration(model_name="gpt-4.1-mini"),
        )


def test_openai_compatible_model_gateway_maps_connection_failure() -> None:
    model_gateway = OpenAiCompatibleModelGateway(
        base_url="https://example.invalid/v1",
        api_key="test-api-key",
        transport=FailingTransport(),
    )

    with pytest.raises(ModelConnectionError, match="Unable to reach model API"):
        model_gateway.generate_structured_improve_response(
            rendered_prompt=RenderedPrompt(
                module_id="module-evaluation-default",
                module_type=PromptModuleType.EVALUATION,
                prompt_text="Evaluate the prompt and return JSON only.",
            ),
            execution_configuration=ExecutionConfiguration(model_name="gpt-4.1-mini"),
        )


def test_openai_compatible_model_gateway_rejects_invalid_response_shape() -> None:
    transport = RecordingTransport(
        response=ModelHttpResponse(status_code=200, body={"choices": []})
    )
    model_gateway = OpenAiCompatibleModelGateway(
        base_url="https://example.invalid/v1",
        api_key="test-api-key",
        transport=transport,
    )

    with pytest.raises(ModelGatewayResponseError, match="choices\\[0\\]"):
        model_gateway.generate_structured_improve_response(
            rendered_prompt=RenderedPrompt(
                module_id="module-evaluation-default",
                module_type=PromptModuleType.EVALUATION,
                prompt_text="Evaluate the prompt and return JSON only.",
            ),
            execution_configuration=ExecutionConfiguration(model_name="gpt-4.1-mini"),
        )


class RecordingTransport:
    def __init__(self, *, response: ModelHttpResponse) -> None:
        self.response = response
        self.recorded_request: ModelHttpRequest | None = None

    def send(self, request: ModelHttpRequest) -> ModelHttpResponse:
        self.recorded_request = request
        return self.response


class FailingTransport:
    def send(self, request: ModelHttpRequest) -> ModelHttpResponse:
        del request
        raise TransportConnectionError("connection timed out")
