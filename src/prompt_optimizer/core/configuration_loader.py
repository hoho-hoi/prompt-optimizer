from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from prompt_optimizer.core.configuration_models import (
    ApplicationSetting,
    ConfigurationValidationError,
    ExecutionConfiguration,
    ModelApiConfiguration,
    OutputFormat,
)


def normalize_execution_configuration_payload(payload: object) -> ExecutionConfiguration:
    """Normalize raw JSON data into an `ExecutionConfiguration`.

    Args:
        payload: Parsed JSON payload expected to contain execution configuration fields.

    Returns:
        ExecutionConfiguration: The validated execution configuration.

    Raises:
        ConfigurationValidationError: If the payload shape or field values are invalid.
    """
    if not isinstance(payload, dict):
        raise ConfigurationValidationError("Execution configuration must be a valid JSON object.")

    allowed_field_names = {
        "configurationId",
        "modelName",
        "allowNoChange",
        "strictMinimalEdit",
        "preferShort",
        "outputFormat",
    }
    unknown_field_names = sorted(set(payload) - allowed_field_names)
    if unknown_field_names:
        unknown_fields = ", ".join(unknown_field_names)
        raise ConfigurationValidationError(
            f"Unknown execution configuration fields: {unknown_fields}."
        )

    configuration_id = _normalize_optional_text_field(payload, "configurationId")
    model_name = _normalize_optional_text_field(payload, "modelName")
    allow_no_change = _normalize_required_boolean_field(payload, "allowNoChange")
    strict_minimal_edit = _normalize_required_boolean_field(payload, "strictMinimalEdit")
    prefer_short = _normalize_required_boolean_field(payload, "preferShort")
    output_format = _normalize_output_format_field(payload)

    if configuration_id is None:
        return ExecutionConfiguration(
            model_name=model_name,
            allow_no_change=allow_no_change,
            strict_minimal_edit=strict_minimal_edit,
            prefer_short=prefer_short,
            output_format=output_format,
        )

    return ExecutionConfiguration(
        configuration_id=configuration_id,
        model_name=model_name,
        allow_no_change=allow_no_change,
        strict_minimal_edit=strict_minimal_edit,
        prefer_short=prefer_short,
        output_format=output_format,
    )


def load_execution_configuration_from_text(input_text: str) -> ExecutionConfiguration:
    """Parse and normalize an execution configuration from text.

    Args:
        input_text: Raw JSON text.

    Returns:
        ExecutionConfiguration: The validated execution configuration.

    Raises:
        ConfigurationValidationError: If the text is empty or invalid.
    """
    payload = _load_json_object_from_text(
        input_text=input_text,
        empty_message="Execution configuration must contain a valid JSON object.",
        invalid_message="Execution configuration must be a valid JSON object.",
    )
    return normalize_execution_configuration_payload(payload)


def load_execution_configuration_from_file(
    execution_configuration_file_path: Path,
) -> ExecutionConfiguration:
    """Load and normalize an execution configuration from a JSON file.

    Args:
        execution_configuration_file_path: File path that should contain a JSON payload.

    Returns:
        ExecutionConfiguration: The validated execution configuration.

    Raises:
        ConfigurationValidationError: If the file cannot be read or parsed.
    """
    input_text = _read_text_file(
        file_path=execution_configuration_file_path,
        error_prefix="Unable to read execution configuration file",
    )
    return load_execution_configuration_from_text(input_text)


def normalize_application_setting_payload(payload: object) -> ApplicationSetting:
    """Normalize raw JSON data into an `ApplicationSetting`.

    Args:
        payload: Parsed JSON payload expected to contain application setting fields.

    Returns:
        ApplicationSetting: The validated application setting.

    Raises:
        ConfigurationValidationError: If the payload shape or field values are invalid.
    """
    if not isinstance(payload, dict):
        raise ConfigurationValidationError("Application setting must be a valid JSON object.")

    allowed_field_names = {
        "settingId",
        "outputLanguage",
        "concisenessPriority",
        "minimalEditStrength",
        "apiSettingRef",
    }
    unknown_field_names = sorted(set(payload) - allowed_field_names)
    if unknown_field_names:
        unknown_fields = ", ".join(unknown_field_names)
        raise ConfigurationValidationError(f"Unknown application setting fields: {unknown_fields}.")

    setting_id = _normalize_optional_text_field(payload, "settingId")
    output_language = _normalize_required_text_field(payload, "outputLanguage")
    conciseness_priority = _normalize_required_text_field(payload, "concisenessPriority")
    minimal_edit_strength = _normalize_required_text_field(payload, "minimalEditStrength")
    api_setting_ref = _normalize_required_text_field(payload, "apiSettingRef")

    if setting_id is None:
        return ApplicationSetting(
            output_language=output_language,
            conciseness_priority=conciseness_priority,
            minimal_edit_strength=minimal_edit_strength,
            api_setting_ref=api_setting_ref,
        )

    return ApplicationSetting(
        setting_id=setting_id,
        output_language=output_language,
        conciseness_priority=conciseness_priority,
        minimal_edit_strength=minimal_edit_strength,
        api_setting_ref=api_setting_ref,
    )


def load_application_setting_from_text(input_text: str) -> ApplicationSetting:
    """Parse and normalize an application setting from text.

    Args:
        input_text: Raw JSON text.

    Returns:
        ApplicationSetting: The validated application setting.

    Raises:
        ConfigurationValidationError: If the text is empty or invalid.
    """
    payload = _load_json_object_from_text(
        input_text=input_text,
        empty_message="Application setting must contain a valid JSON object.",
        invalid_message="Application setting must be a valid JSON object.",
    )
    return normalize_application_setting_payload(payload)


def load_application_setting_from_file(application_setting_file_path: Path) -> ApplicationSetting:
    """Load and normalize an application setting from a JSON file.

    Args:
        application_setting_file_path: File path that should contain a JSON payload.

    Returns:
        ApplicationSetting: The validated application setting.

    Raises:
        ConfigurationValidationError: If the file cannot be read or parsed.
    """
    input_text = _read_text_file(
        file_path=application_setting_file_path,
        error_prefix="Unable to read application setting file",
    )
    return load_application_setting_from_text(input_text)


def load_model_api_configuration(
    *,
    application_setting: ApplicationSetting,
    environment_variables: Mapping[str, str],
) -> ModelApiConfiguration:
    """Resolve model API settings from an application setting secret reference.

    Args:
        application_setting: Persisted application setting that contains `api_setting_ref`.
        environment_variables: Environment variable mapping used for env-based resolution.

    Returns:
        ModelApiConfiguration: Resolved connection settings for the model API.

    Raises:
        ConfigurationValidationError: If the secret reference is invalid or incomplete.
    """
    api_setting_ref = application_setting.api_setting_ref.strip()

    if api_setting_ref.startswith("env:"):
        env_prefix = api_setting_ref.removeprefix("env:").strip()
        if not env_prefix:
            raise ConfigurationValidationError("api_setting_ref env prefix must not be empty.")
        return _load_model_api_configuration_from_environment(
            env_prefix=env_prefix,
            environment_variables=environment_variables,
        )

    if api_setting_ref.startswith("local:"):
        local_file_path_text = api_setting_ref.removeprefix("local:").strip()
        if not local_file_path_text:
            raise ConfigurationValidationError("api_setting_ref local path must not be empty.")
        return _load_model_api_configuration_from_local_file(Path(local_file_path_text))

    raise ConfigurationValidationError(
        "api_setting_ref must use 'env:<PREFIX>' or 'local:<PATH>' syntax."
    )


def _load_model_api_configuration_from_environment(
    *, env_prefix: str, environment_variables: Mapping[str, str]
) -> ModelApiConfiguration:
    base_url_key = f"{env_prefix}_BASE_URL"
    api_key_key = f"{env_prefix}_API_KEY"

    base_url = environment_variables.get(base_url_key)
    if base_url is None or not base_url.strip():
        raise ConfigurationValidationError(f"{base_url_key} is required for api_setting_ref.")

    api_key = environment_variables.get(api_key_key)
    if api_key is None or not api_key.strip():
        raise ConfigurationValidationError(f"{api_key_key} is required for api_setting_ref.")

    return ModelApiConfiguration(base_url=base_url.strip(), api_key=api_key.strip())


def _load_model_api_configuration_from_local_file(local_file_path: Path) -> ModelApiConfiguration:
    input_text = _read_text_file(
        file_path=local_file_path,
        error_prefix="Unable to read local API setting file",
    )
    payload = _load_json_object_from_text(
        input_text=input_text,
        empty_message="Local API setting must contain a valid JSON object.",
        invalid_message="Local API setting must be a valid JSON object.",
    )
    return _normalize_model_api_configuration_payload(payload)


def _normalize_model_api_configuration_payload(payload: object) -> ModelApiConfiguration:
    if not isinstance(payload, dict):
        raise ConfigurationValidationError("Local API setting must be a valid JSON object.")

    allowed_field_names = {"baseUrl", "apiKey"}
    unknown_field_names = sorted(set(payload) - allowed_field_names)
    if unknown_field_names:
        unknown_fields = ", ".join(unknown_field_names)
        raise ConfigurationValidationError(f"Unknown local API setting fields: {unknown_fields}.")

    base_url = _normalize_required_text_field(payload, "baseUrl")
    api_key = _normalize_required_text_field(payload, "apiKey")
    return ModelApiConfiguration(base_url=base_url, api_key=api_key)


def _load_json_object_from_text(
    *, input_text: str, empty_message: str, invalid_message: str
) -> object:
    if not input_text.strip():
        raise ConfigurationValidationError(empty_message)

    try:
        return json.loads(input_text)
    except json.JSONDecodeError as error:
        raise ConfigurationValidationError(invalid_message) from error


def _read_text_file(*, file_path: Path, error_prefix: str) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigurationValidationError(f"{error_prefix}: {file_path}.") from error


def _normalize_required_text_field(payload: dict[object, object], field_name: str) -> str:
    if field_name not in payload:
        raise ConfigurationValidationError(f"{field_name} is required.")

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise ConfigurationValidationError(f"{field_name} must be a string.")

    normalized_value = field_value.strip()
    if not normalized_value:
        raise ConfigurationValidationError(f"{field_name} must not be empty.")

    return normalized_value


def _normalize_optional_text_field(payload: dict[object, object], field_name: str) -> str | None:
    if field_name not in payload or payload[field_name] is None:
        return None

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise ConfigurationValidationError(f"{field_name} must be a string.")

    normalized_value = field_value.strip()
    if not normalized_value:
        raise ConfigurationValidationError(f"{field_name} must not be empty when provided.")

    return normalized_value


def _normalize_required_boolean_field(payload: dict[object, object], field_name: str) -> bool:
    if field_name not in payload:
        raise ConfigurationValidationError(f"{field_name} is required.")

    field_value = payload[field_name]
    if not isinstance(field_value, bool):
        raise ConfigurationValidationError(f"{field_name} must be a boolean.")

    return field_value


def _normalize_output_format_field(payload: dict[object, object]) -> OutputFormat:
    raw_output_format = _normalize_required_text_field(payload, "outputFormat")

    try:
        return OutputFormat(raw_output_format)
    except ValueError as error:
        allowed_output_formats = ", ".join(output_format.value for output_format in OutputFormat)
        raise ConfigurationValidationError(
            f"outputFormat must be one of: {allowed_output_formats}."
        ) from error
