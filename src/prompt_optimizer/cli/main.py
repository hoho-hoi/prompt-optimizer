import typer

from prompt_optimizer.core import create_application_metadata

application_metadata = create_application_metadata()
application_cli = typer.Typer(
    add_completion=False,
    help=application_metadata.application_summary,
    no_args_is_help=True,
)


@application_cli.callback()
def execute_application() -> None:
    """Expose the top-level CLI command group.

    Returns:
        None: Typer handles parsing and help rendering.
    """
    return None


def main() -> None:
    """Run the prompt improver console script.

    Returns:
        None: Delegates command execution to Typer.
    """
    application_cli()
