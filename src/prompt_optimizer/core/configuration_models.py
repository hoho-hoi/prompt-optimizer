from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class ConfigurationValidationError(ValueError):
    """Raise when configuration payloads violate required invariants."""


class OutputFormat(StrEnum):
    """Represent supported output serialization formats."""

    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"


@dataclass(frozen=True, slots=True, kw_only=True)
class ExecutionConfiguration:
    """Represent runtime options for a model-backed improve execution.

    Attributes:
        configuration_id: Stable identifier for the execution configuration.
        model_name: Optional model name used by the selected gateway.
        allow_no_change: Whether the model may conclude no edit is required.
        strict_minimal_edit: Whether the model should minimize edits aggressively.
        prefer_short: Whether the model should prefer shorter prompts when possible.
        output_format: Desired response serialization format.
    """

    configuration_id: str = field(default_factory=lambda: str(uuid4()))
    model_name: str | None = None
    allow_no_change: bool = True
    strict_minimal_edit: bool = False
    prefer_short: bool = False
    output_format: OutputFormat = OutputFormat.JSON

    def __post_init__(self) -> None:
        """Validate execution configuration fields after construction."""
        _require_non_empty_text(self.configuration_id, "configuration_id")
        if self.model_name is not None:
            _require_non_empty_text(self.model_name, "model_name")

    def to_payload(self) -> dict[str, object]:
        """Serialize the configuration using the public JSON field names.

        Returns:
            dict[str, object]: JSON-serializable execution configuration payload.
        """
        return {
            "configurationId": self.configuration_id,
            "modelName": self.model_name,
            "allowNoChange": self.allow_no_change,
            "strictMinimalEdit": self.strict_minimal_edit,
            "preferShort": self.prefer_short,
            "outputFormat": self.output_format.value,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ApplicationSetting:
    """Represent persisted application-level defaults and secret references.

    Attributes:
        setting_id: Stable identifier for the application setting record.
        output_language: Preferred language for user-facing output.
        conciseness_priority: User-selected conciseness preference descriptor.
        minimal_edit_strength: User-selected minimal edit preference descriptor.
        api_setting_ref: Secret reference in `env:<PREFIX>` or `local:<PATH>` form.
    """

    setting_id: str = field(default_factory=lambda: str(uuid4()))
    output_language: str
    conciseness_priority: str
    minimal_edit_strength: str
    api_setting_ref: str

    def __post_init__(self) -> None:
        """Validate application setting fields after construction."""
        _require_non_empty_text(self.setting_id, "setting_id")
        _require_non_empty_text(self.output_language, "output_language")
        _require_non_empty_text(self.conciseness_priority, "conciseness_priority")
        _require_non_empty_text(self.minimal_edit_strength, "minimal_edit_strength")
        _require_non_empty_text(self.api_setting_ref, "api_setting_ref")

    def to_payload(self) -> dict[str, str]:
        """Serialize the application setting using public JSON field names.

        Returns:
            dict[str, str]: JSON-serializable application setting payload.
        """
        return {
            "settingId": self.setting_id,
            "outputLanguage": self.output_language,
            "concisenessPriority": self.conciseness_priority,
            "minimalEditStrength": self.minimal_edit_strength,
            "apiSettingRef": self.api_setting_ref,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelApiConfiguration:
    """Represent resolved API connection settings for a model gateway.

    Attributes:
        base_url: Base URL of the OpenAI-compatible API endpoint.
        api_key: Secret token used for authorization.
    """

    base_url: str
    api_key: str

    def __post_init__(self) -> None:
        """Validate resolved API configuration fields."""
        _require_non_empty_text(self.base_url, "base_url")
        _require_non_empty_text(self.api_key, "api_key")


def _require_non_empty_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ConfigurationValidationError(f"{field_name} must not be empty.")
