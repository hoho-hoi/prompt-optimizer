from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from prompt_optimizer.core import (
    InputValidationError,
    create_application_metadata,
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
    """Load and validate an improve request payload.

    Args:
        input_file_path: Optional file path for a JSON payload. When omitted,
            the command reads from standard input.

    Returns:
        None: Writes the normalized payload to standard output.
    """
    try:
        if input_file_path is not None:
            normalized_request = load_improve_request_from_file(input_file_path)
        else:
            normalized_request = load_improve_request_from_text(sys.stdin.read())
    except InputValidationError as error:
        typer.echo(f"Input validation error: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(
        json.dumps(
            {"request": normalized_request.to_payload()},
            ensure_ascii=False,
        )
    )


def main() -> None:
    """Run the prompt improver console script.

    Returns:
        None: Delegates command execution to Typer.
    """
    application_cli()
