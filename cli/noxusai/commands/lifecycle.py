from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import typer
from rich.prompt import Confirm

from noxusai.context import runtime
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import load_project
from noxusai.services.lifecycle import lifecycle_action


def init_command(
    ctx: typer.Context,
    bench: Path = typer.Option(Path("."), "--bench"),
    site: str | None = typer.Option(None, "--site"),
) -> None:
    state = runtime(ctx)
    from noxusai.services.lifecycle import initialize_existing

    result = initialize_existing(state, bench.resolve(), site=site)
    state.emit("init", result)


def action_command(action: str) -> Callable[[typer.Context], None]:
    def command(ctx: typer.Context) -> None:
        state = runtime(ctx)
        project = load_project(state.cwd)
        result = lifecycle_action(state, project, action)
        state.emit(action, result)

    command.__name__ = f"{action}_command"
    return command


dev_command = action_command("dev")
start_command = action_command("start")
stop_command = action_command("stop")
status_command = action_command("status")
logs_command = action_command("logs")
test_command = action_command("test")
update_command = action_command("update")
backup_command = action_command("backup")


def restore_command(
    ctx: typer.Context,
    archive: Path = typer.Option(..., "--archive"),
    target: str = typer.Option(..., "--target", help="Exact site or database identifier."),
    confirm_target: str | None = typer.Option(None, "--confirm-target"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    state = runtime(ctx)
    project = load_project(state.cwd)
    resolved = archive.resolve()
    expected = project.site_name or (
        "noxus" if project.project_type.value == "website" else f"{project.name}.localhost"
    )
    if target != expected:
        raise NoxusError(f"Target must exactly match {expected}", exit_code=ExitCode.UNSAFE)
    if yes and confirm_target != expected:
        raise NoxusError(
            f"Noninteractive restore requires --confirm-target {expected}",
            exit_code=ExitCode.UNSAFE,
        )
    if not yes:
        state.console.print(
            f"Project: {project.root}\nTarget: {expected}\nArchive: {resolved}\n"
            "A safety backup will be created first."
        )
        if not Confirm.ask("Restore this exact target?", default=False):
            raise typer.Exit(ExitCode.CANCELLED)
    from noxusai.services.lifecycle import restore_backup

    result = restore_backup(state, project, archive=resolved, target_identifier=target)
    state.emit("restore", result)
