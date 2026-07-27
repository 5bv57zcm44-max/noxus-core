from __future__ import annotations

import typer
from pydantic import ValidationError

from noxusai.context import runtime
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import load_project, merged_config, redacted_config

app = typer.Typer(help="Inspect and validate NOXUS configuration.")


@app.command("show")
def show(ctx: typer.Context) -> None:
    state = runtime(ctx)
    try:
        project = load_project(state.cwd)
    except NoxusError:
        project = None
    state.emit("config show", redacted_config(merged_config(project)))


@app.command("validate")
def validate(ctx: typer.Context) -> None:
    state = runtime(ctx)
    try:
        config = load_project(state.cwd)
    except (NoxusError, ValidationError) as exc:
        state.console.print(f"[red]Invalid configuration:[/red] {exc}")
        raise typer.Exit(ExitCode.USAGE) from exc
    state.emit(
        "config validate",
        {"valid": True, "project": config.name, "type": config.project_type.value},
    )
