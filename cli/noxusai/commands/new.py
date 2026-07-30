from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from noxusai.context import RuntimeContext, runtime
from noxusai.errors import ExitCode, NoxusError
from noxusai.validators.names import contained_destination, project_slug

app = typer.Typer(
    help="Create a website backend or modular SaaS system.", invoke_without_command=True
)


def _csv(value: str) -> list[str]:
    return [item.strip().lower().replace("-", "_") for item in value.split(",") if item.strip()]


def _project_name(state: RuntimeContext, value: str | None, *, default: str) -> str:
    """Return a validated slug and keep interactive validation user-friendly."""
    if value is not None:
        try:
            return project_slug(value)
        except ValueError as exc:
            raise NoxusError(str(exc), exit_code=ExitCode.USAGE) from exc
    if state.json_output:
        raise NoxusError("--name is required with --json", exit_code=ExitCode.USAGE)
    while True:
        candidate = Prompt.ask("Project name", default=default)
        try:
            return project_slug(candidate)
        except ValueError as exc:
            state.console.print(f"[red]Invalid project name:[/red] {exc}")


def _project_target(directory: Path, name: str) -> Path:
    try:
        return contained_destination(directory, name)
    except ValueError as exc:
        raise NoxusError(str(exc), exit_code=ExitCode.UNSAFE) from exc


@app.callback()
def new_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return
    state = runtime(ctx)
    if state.json_output:
        raise NoxusError("Interactive wizard is unavailable with --json", exit_code=ExitCode.USAGE)
    state.console.print(
        Panel.fit(
            "1. Company Website Backend\n"
            "2. Modular SaaS Business System\n"
            "3. Install NOXUS CORE in an existing Frappe site\n"
            "4. Create a NOXUS module\n"
            "5. Manage an existing NOXUS project",
            title="What would you like to build?",
        )
    )
    choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"], default="1")
    if choice == "1":
        ctx.invoke(website)
    elif choice == "2":
        ctx.invoke(saas)
    elif choice == "3":
        from noxusai.commands.lifecycle import init_command

        ctx.invoke(init_command)
    elif choice == "4":
        from noxusai.commands.module import create

        name = Prompt.ask("Module name")
        ctx.invoke(create, module_name=name)
    else:
        state.console.print("Run `noxusai status`, `start`, `stop`, `logs`, `backup`, or `update`.")


@app.command("website")
def website(
    ctx: typer.Context,
    name: str | None = typer.Option(None, "--name", help="Lowercase project slug."),
    directory: Path = typer.Option(Path("."), "--directory", help="Parent output directory."),
    database: Literal["postgres", "sqlite"] = typer.Option("postgres", help="postgres or sqlite"),
    auth: Literal["jwt", "session", "both"] = typer.Option("both", help="jwt, session, or both"),
    language: Literal["english", "arabic", "both"] = typer.Option(
        "both", help="english, arabic, or both"
    ),
    modules: str = typer.Option("company,website,services,portfolio,team,contact,seo,media"),
    docker: bool = typer.Option(True, "--docker/--no-docker"),
    git: bool = typer.Option(False, "--git/--no-git"),
    start: bool = typer.Option(False, "--start/--no-start"),
    yes: bool = typer.Option(False, "--yes", help="Accept the displayed plan."),
) -> None:
    state = runtime(ctx)
    normalized = _project_name(state, name, default="company-website")
    target = _project_target(directory, normalized)
    selection = _csv(modules)
    summary = {
        "type": "website",
        "name": normalized,
        "target": str(target),
        "environment": "development",
        "language": language,
        "database": database,
        "authentication": auth,
        "modules": selection,
        "docker": docker,
        "git": git,
        "start": start,
    }
    if not state.json_output:
        state.console.print(
            Panel.fit(
                "\n".join(f"{key}: {value}" for key, value in summary.items()),
                title="Creation plan",
            )
        )
    if not yes and not state.dry_run and not Confirm.ask("Create this project?", default=False):
        raise typer.Exit(ExitCode.CANCELLED)
    from noxusai.services.website_generator import generate_website

    result = generate_website(
        state,
        target=target,
        name=normalized,
        database=database,
        authentication=auth,
        language=language,
        modules=selection,
        docker=docker,
        initialize_git=git,
        start=start,
    )
    state.emit("new website", result)


@app.command("saas")
def saas(
    ctx: typer.Context,
    name: str | None = typer.Option(None, "--name"),
    directory: Path = typer.Option(Path("."), "--directory"),
    industry: str = typer.Option("general-business"),
    modules: str = typer.Option("crm,inventory,projects,support"),
    language: Literal["english", "arabic", "both"] = typer.Option("both"),
    with_erpnext: bool = typer.Option(False, "--with-erpnext/--without-erpnext"),
    docker: bool = typer.Option(True, "--docker/--no-docker"),
    edge: bool = typer.Option(False, "--edge"),
    repository_url: str | None = typer.Option(None, "--repository-url"),
    branch: str | None = typer.Option(
        None, "--branch", help="Exact development branch for --edge."
    ),
    admin_secret_file: Path | None = typer.Option(
        None,
        "--admin-secret-file",
        help="Protected file containing the initial administrator password.",
    ),
    start: bool = typer.Option(False, "--start/--no-start"),
    yes: bool = typer.Option(False, "--yes"),
) -> None:
    state = runtime(ctx)
    if edge and (not repository_url or not branch):
        raise NoxusError("--edge requires --repository-url and --branch", exit_code=ExitCode.USAGE)
    if not edge and (repository_url or branch):
        raise NoxusError(
            "--repository-url and --branch are only valid with --edge", exit_code=ExitCode.USAGE
        )
    normalized = _project_name(state, name, default="noxus-business")
    target = _project_target(directory, normalized)
    selection = _csv(modules)
    summary = {
        "type": "saas",
        "name": normalized,
        "target": str(target),
        "industry": industry,
        "language": language,
        "modules": selection,
        "erpnext": with_erpnext,
        "docker": docker,
        "source": repository_url if edge else "bundled wheel payload",
        "branch": branch,
        "administrator_secret": str(admin_secret_file.resolve())
        if admin_secret_file
        else "NOXUS_ADMIN_PASSWORD",
        "start": start,
    }
    if not state.json_output:
        state.console.print(
            Panel.fit(
                "\n".join(f"{key}: {value}" for key, value in summary.items()),
                title="Creation plan",
            )
        )
    if not yes and not state.dry_run and not Confirm.ask("Create this project?", default=False):
        raise typer.Exit(ExitCode.CANCELLED)
    from noxusai.services.saas_generator import generate_saas

    result = generate_saas(
        state,
        target=target,
        name=normalized,
        industry=industry,
        language=language,
        modules=selection,
        with_erpnext=with_erpnext,
        edge_repository=repository_url if edge else None,
        edge_branch=branch if edge else None,
        admin_secret_file=admin_secret_file,
        docker=docker,
        start=start,
    )
    state.emit("new saas", result)
