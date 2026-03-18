from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from prompt_optimizer.core import (
    ConfigurationValidationError,
    InputValidationError,
    ModelGatewayError,
    ResponseValidationError,
    create_application_metadata,
    create_default_improve_service,
    load_improve_request_from_file,
    load_improve_request_from_text,
)

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


@application_cli.command("improve")
def improve_prompt(
    input_file_path: Annotated[
        Path | None,
        typer.Option(
            "--input",
            file_okay=True,
            dir_okay=False,
            exists=True,
            readable=True,
            help="Path to a JSON file that contains an improve request payload.",
        ),
    ] = None,
) -> None:
    """Execute the improve command from file input or standard input.

    Args:
        input_file_path: Optional file path for a JSON payload. When omitted,
            the command reads from standard input.

    Returns:
        None: Writes the structured improve result to standard output.
    """
    try:
        if input_file_path is not None:
            normalized_request = load_improve_request_from_file(input_file_path)
        else:
            normalized_request = load_improve_request_from_text(sys.stdin.read())

        improve_service = create_default_improve_service()
        improve_result = improve_service.execute_improve_request(normalized_request)
    except InputValidationError as error:
        typer.echo(f"Input validation error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except ConfigurationValidationError as error:
        typer.echo(f"Configuration error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except ResponseValidationError as error:
        typer.echo(f"Response validation error: {error}", err=True)
        raise typer.Exit(code=1) from error
    except ModelGatewayError as error:
        typer.echo(f"Model execution error: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(
        json.dumps(
            {
                "judgment": improve_result.judgment.value,
                "reason": improve_result.reason,
                "improved_prompt": improve_result.improved_prompt,
                "changes": improve_result.changes_summary,
            },
            ensure_ascii=False,
        )
    )


def main() -> None:
    """Run the prompt improver console script.

    Returns:
        None: Delegates command execution to Typer.
    """
    application_cli()
