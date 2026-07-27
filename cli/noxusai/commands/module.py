from __future__ import annotations

from pathlib import Path

import typer
from noxus_module_sdk.io import load_yaml
from noxus_module_sdk.manifest import ModuleManifest
from noxus_module_sdk.resolver import DependencyResolver, ResolutionError
from pydantic import ValidationError
from rich.prompt import Confirm

from noxusai.context import runtime
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import load_project

app = typer.Typer(help="Create, inspect, validate, install, and uninstall NOXUS modules.")


def _manifest_path(value: str, start: Path) -> Path:
    direct = Path(value)
    candidates = [
        direct / "noxus-module.yml",
        start / value / "noxus-module.yml",
        start / "frappe_apps" / value / "noxus-module.yml",
    ]
    if direct.name == "noxus-module.yml":
        candidates.insert(0, direct)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise NoxusError(f"No manifest found for {value}", exit_code=ExitCode.USAGE)


@app.command("create")
def create(
    ctx: typer.Context,
    module_name: str,
    directory: Path = typer.Option(Path("."), "--directory"),
) -> None:
    state = runtime(ctx)
    from noxusai.services.module_generator import generate_module

    result = generate_module(state, module_name, directory)
    state.emit("module create", result)


@app.command("list")
def list_modules(ctx: typer.Context) -> None:
    state = runtime(ctx)
    paths = sorted(state.cwd.glob("frappe_apps/*/noxus-module.yml"))
    items = []
    for path in paths:
        try:
            value = load_yaml(path, ModuleManifest)
            items.append(
                {"name": value.name, "version": value.version, "category": value.category.value}
            )
        except (ValueError, ValidationError) as exc:
            items.append({"name": path.parent.name, "error": str(exc)})
    state.emit("module list", items)


@app.command("validate")
def validate(ctx: typer.Context, module_name: str) -> None:
    state = runtime(ctx)
    try:
        value = load_yaml(_manifest_path(module_name, state.cwd), ModuleManifest)
    except (ValueError, ValidationError) as exc:
        state.console.print(f"[red]Invalid manifest:[/red] {exc}")
        raise typer.Exit(ExitCode.USAGE) from exc
    state.emit("module validate", {"valid": True, "name": value.name, "version": value.version})


def _catalog(start: Path) -> list[ModuleManifest]:
    return [
        load_yaml(path, ModuleManifest)
        for path in sorted(start.glob("frappe_apps/*/noxus-module.yml"))
    ]


@app.command("install")
def install(
    ctx: typer.Context,
    module_name: str,
    site: str | None = typer.Option(None, "--site"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    state = runtime(ctx)
    project = load_project(state.cwd)
    requested = module_name if module_name.startswith("noxus_") else f"noxus_{module_name}"
    try:
        resolution = DependencyResolver(
            _catalog(project.root),
            erpnext_version="16.29.0" if project.with_erpnext else None,
        ).resolve([requested])
    except ResolutionError as exc:
        raise NoxusError(str(exc), exit_code=ExitCode.CONFLICT) from exc
    order = [item.name for item in resolution.installation_order]
    if (
        not yes
        and not state.dry_run
        and not Confirm.ask(f"Install {', '.join(order)}?", default=False)
    ):
        raise typer.Exit(ExitCode.CANCELLED)
    from noxusai.services.lifecycle import install_modules

    install_modules(state, project, order, site=site)
    state.emit("module install", {"installed": order}, warnings=resolution.warnings)


@app.command("uninstall")
def uninstall(
    ctx: typer.Context,
    module_name: str,
    site: str = typer.Option(..., "--site"),
    confirm_target: str | None = typer.Option(None, "--confirm-target"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    state = runtime(ctx)
    project = load_project(state.cwd)
    normalized = module_name if module_name.startswith("noxus_") else f"noxus_{module_name}"
    target = f"{site}:{normalized}"
    if yes and confirm_target != target:
        raise NoxusError(
            f"Noninteractive uninstall requires --confirm-target {target}",
            exit_code=ExitCode.UNSAFE,
        )
    if not yes and not Confirm.ask(
        f"Uninstall {normalized} from site {site} and delete its data?", default=False
    ):
        raise typer.Exit(ExitCode.CANCELLED)
    from noxusai.services.lifecycle import uninstall_module

    uninstall_module(state, project, normalized, site=site)
    state.emit("module uninstall", {"uninstalled": normalized, "site": site})
