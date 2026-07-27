from __future__ import annotations

import json

import typer

from noxusai import __version__
from noxusai.commands import config, module, new
from noxusai.commands.doctor import doctor_command
from noxusai.commands.lifecycle import (
    backup_command,
    dev_command,
    init_command,
    logs_command,
    restore_command,
    start_command,
    status_command,
    stop_command,
    test_command,
    update_command,
)
from noxusai.context import RuntimeContext
from noxusai.errors import NoxusError

app = typer.Typer(
    name="noxusai",
    help="Generate secure website backends and modular Frappe business systems.",
    no_args_is_help=False,
    pretty_exceptions_show_locals=False,
)
app.add_typer(new.app, name="new")
app.add_typer(module.app, name="module")
app.add_typer(config.app, name="config")
app.command("doctor")(doctor_command)
app.command("init")(init_command)
app.command("dev")(dev_command)
app.command("start")(start_command)
app.command("stop")(stop_command)
app.command("status")(status_command)
app.command("logs")(logs_command)
app.command("test")(test_command)
app.command("update")(update_command)
app.command("backup")(backup_command)
app.command("restore")(restore_command)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the installed NOXUS version.",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Describe changes without applying them."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable output."),
    no_color: bool = typer.Option(False, "--no-color"),
) -> None:
    del version
    ctx.obj = RuntimeContext(
        dry_run=dry_run,
        verbose=verbose,
        json_output=json_output,
        no_color=no_color,
    )


def run() -> None:
    try:
        app()
    except NoxusError as exc:
        typer.echo(
            json.dumps(
                {
                    "ok": False,
                    "command": None,
                    "data": None,
                    "warnings": [],
                    "error": {"message": str(exc), "code": int(exc.exit_code)},
                }
            ),
            err=True,
        )
        raise typer.Exit(exc.exit_code) from exc


if __name__ == "__main__":
    run()
