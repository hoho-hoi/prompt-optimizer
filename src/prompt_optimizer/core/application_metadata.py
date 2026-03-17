from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApplicationMetadata:
    """Represent stable metadata consumed by the CLI layer."""

    application_name: str
    application_summary: str


def create_application_metadata() -> ApplicationMetadata:
    """Create metadata for the prompt improver application.

    Returns:
        ApplicationMetadata: Stable metadata used by the CLI entry point.
    """
    return ApplicationMetadata(
        application_name="prompt-improver",
        application_summary="Improve prompts with a maintainable CLI foundation.",
    )
