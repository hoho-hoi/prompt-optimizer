from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from prompt_optimizer.core.improvement_models import DomainValidationError, ImproveRequest


class PromptModuleType(StrEnum):
    """Represent supported replaceable prompt module categories."""

    SYSTEM = "system"
    EVALUATION = "evaluation"
    FORMATTING = "formatting"
    TEST_JUDGE = "test_judge"


@dataclass(frozen=True, slots=True, kw_only=True)
class RenderedPrompt:
    """Represent the rendered prompt text produced by a prompt module.

    Attributes:
        module_id: Stable identifier of the prompt module that rendered the output.
        module_type: Category of the prompt module.
        prompt_text: Final prompt text to send to a downstream engine.
    """

    module_id: str
    module_type: PromptModuleType
    prompt_text: str

    def __post_init__(self) -> None:
        """Validate required rendered prompt attributes."""
        _require_non_empty_text(self.module_id, "module_id")
        _require_non_empty_text(self.prompt_text, "prompt_text")


@dataclass(frozen=True, slots=True, kw_only=True)
class PromptModule:
    """Represent a replaceable prompt module definition.

    Attributes:
        module_id: Stable identifier for the module definition.
        module_type: Category that describes the module role.
        prompt_body: Base instruction body that anchors rendered prompts.
    """

    module_id: str
    module_type: PromptModuleType
    prompt_body: str

    def __post_init__(self) -> None:
        """Validate required prompt module attributes."""
        _require_non_empty_text(self.module_id, "module_id")
        _require_non_empty_text(self.prompt_body, "prompt_body")

    def render_prompt(self, improve_request: ImproveRequest) -> RenderedPrompt:
        """Render the prompt module with request-specific context.

        Args:
            improve_request: Normalized request used to construct the engine input.

        Returns:
            RenderedPrompt: A prompt bundle that keeps module metadata with the text.
        """
        prompt_sections: list[str] = [
            self.prompt_body.strip(),
            "Original Prompt:\n" + improve_request.original_prompt,
        ]

        optional_sections = (
            ("Improvement Requests", improve_request.improvement_requests),
            ("Input/Output Examples", improve_request.io_examples),
            ("Additional Constraints", improve_request.additional_constraints),
        )
        for section_title, section_items in optional_sections:
            if section_items:
                formatted_items = "\n".join(f"- {section_item}" for section_item in section_items)
                prompt_sections.append(f"{section_title}:\n{formatted_items}")

        if improve_request.context is not None:
            prompt_sections.append("Context:\n" + improve_request.context)

        return RenderedPrompt(
            module_id=self.module_id,
            module_type=self.module_type,
            prompt_text="\n\n".join(prompt_sections),
        )


def _require_non_empty_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise DomainValidationError(f"{field_name} must not be empty.")
