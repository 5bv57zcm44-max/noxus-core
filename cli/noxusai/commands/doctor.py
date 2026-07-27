from __future__ import annotations

import typer
from rich.table import Table

from noxusai.context import runtime
from noxusai.errors import ExitCode
from noxusai.services.doctor import run_doctor, serialize_checks


def doctor_command(
    ctx: typer.Context,
    workflow: str = typer.Option("all", help="Check all, website, saas, or edge requirements."),
) -> None:
    state = runtime(ctx)
    checks = run_doctor(state, workflow)
    failed = [check for check in checks if check.required and check.status == "fail"]
    if state.json_output:
        state.emit("doctor", serialize_checks(checks))
    else:
        table = Table(title="NOXUS CORE Environment Check")
        table.add_column("Status", no_wrap=True)
        table.add_column("Check")
        table.add_column("Detail")
        icons = {
            "pass": "[green]✓[/green]",
            "warning": "[yellow]![/yellow]",
            "fail": "[red]✗[/red]",
        }
        for check in checks:
            table.add_row(icons[check.status], check.name, check.detail)
        state.console.print(table)
    if failed:
        raise typer.Exit(ExitCode.PREREQUISITE)
