from __future__ import annotations

import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from noxus_module_sdk.project import ProjectConfig, ProjectType
from noxusai.context import RuntimeContext
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import write_project
from noxusai.services.journal import OperationJournal
from noxusai.services.process import CommandResult, ProcessRunner


def _compose_file(project: ProjectConfig) -> Path:
    candidates = [project.root / "compose.yaml", project.root / "docker-compose.yml"]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise NoxusError("This project has no Docker Compose definition", exit_code=ExitCode.USAGE)


def _compose(
    context: RuntimeContext,
    project: ProjectConfig,
    args: list[str],
    *,
    check: bool = True,
    production: bool = False,
) -> CommandResult:
    compose = _compose_file(project)
    compose_args = ["-f", str(compose)]
    production_override = project.root / "compose.production.yaml"
    if production and production_override.is_file():
        compose_args.extend(["-f", str(production_override)])
    environment = {"NOXUS_DEPLOYMENT_PROFILE": "production"} if production else None
    return ProcessRunner(context).run(
        [
            "docker",
            "compose",
            "--project-directory",
            str(project.root),
            *compose_args,
            *args,
        ],
        cwd=project.root,
        env=environment,
        check=check,
        timeout=900,
    )


def lifecycle_action(
    context: RuntimeContext, project: ProjectConfig, action: str
) -> dict[str, object]:
    journal = OperationJournal(project.root)
    journal.record(action, str(project.root), "started")
    try:
        if action in {"dev", "start"}:
            if project.docker:
                if action == "dev":
                    _compose(context, project, ["--profile", "development", "up", "--build"])
                else:
                    _compose(
                        context,
                        project,
                        ["--profile", "production", "up", "--build", "--detach"],
                        production=True,
                    )
            elif project.project_type is ProjectType.WEBSITE:
                ProcessRunner(context).run(
                    ["python", "manage.py", "runserver"], cwd=project.root, timeout=86400
                )
            else:
                raise NoxusError("Non-Docker SaaS execution is unsupported")
        elif action == "stop":
            _compose(context, project, ["stop"])
        elif action == "status":
            compose_result = _compose(context, project, ["ps", "--format", "json"], check=False)
            journal.record(action, str(project.root), "complete")
            return {
                "project": project.name,
                "services": compose_result.stdout,
                "healthy": compose_result.returncode == 0,
            }
        elif action == "logs":
            compose_result = _compose(context, project, ["logs", "--tail", "200"], check=False)
            journal.record(action, str(project.root), "complete")
            return {
                "project": project.name,
                "logs": compose_result.stdout or compose_result.stderr,
            }
        elif action == "test":
            if project.project_type is ProjectType.WEBSITE:
                if project.docker:
                    _compose(
                        context,
                        project,
                        ["--profile", "development", "run", "--rm", "web", "pytest"],
                    )
                else:
                    ProcessRunner(context).run(["python", "-m", "pytest"], cwd=project.root)
            else:
                site = project.site_name or f"{project.name}.localhost"
                _compose(
                    context, project, ["exec", "backend", "bench", "--site", site, "run-tests"]
                )
        elif action == "backup":
            backup_result = create_backup(context, project)
            journal.record(action, str(project.root), "complete")
            return backup_result
        elif action == "restore":
            raise NoxusError(
                "Restore requires an explicit archive and target; "
                "use the generated recovery instructions.",
                exit_code=ExitCode.UNSAFE,
            )
        elif action == "update":
            if project.project_type is ProjectType.WEBSITE:
                from noxusai.services.website_update import update_generated_website

                update_result = update_generated_website(context, project)
                journal.record(
                    action,
                    str(project.root),
                    "complete-with-conflicts" if update_result["conflicts"] else "complete",
                )
                return update_result
            plan = project.root / ".noxus" / "update-plan.yml"
            if not context.dry_run:
                plan.parent.mkdir(parents=True, exist_ok=True)
                plan.write_text(
                    "status: review-required\n"
                    "reason: project updates never overwrite user changes\n",
                    encoding="utf-8",
                )
            journal.record(action, str(project.root), "review-required")
            return {"project": project.name, "plan": str(plan), "applied": False}
        else:
            raise NoxusError(f"Unsupported lifecycle action: {action}")
    except Exception as exc:
        journal.record(action, str(project.root), "failed", str(exc))
        raise
    journal.record(action, str(project.root), "complete")
    return {"project": project.name, "action": action, "dry_run": context.dry_run}


def create_backup(context: RuntimeContext, project: ProjectConfig) -> dict[str, object]:
    stamp = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    backup_dir = project.root / ".noxus" / "backups" / stamp
    if not context.dry_run:
        backup_dir.mkdir(parents=True, exist_ok=False)
    if project.project_type is ProjectType.WEBSITE:
        if project.docker:
            result = _compose(
                context,
                project,
                ["exec", "-T", "db", "pg_dump", "--clean", "--if-exists", "-U", "noxus", "noxus"],
            )
            archive = backup_dir / "database.sql"
            if not context.dry_run:
                archive.write_text(result.stdout + "\n", encoding="utf-8")
        else:
            source = project.root / "db.sqlite3"
            if not source.is_file() and not context.dry_run:
                raise NoxusError(
                    f"SQLite database does not exist: {source}", exit_code=ExitCode.USAGE
                )
            archive = backup_dir / "database.sqlite3"
            if not context.dry_run:
                shutil.copy2(source, archive)
    else:
        site = project.site_name or f"{project.name}.localhost"
        _compose(
            context,
            project,
            [
                "exec",
                "-T",
                "backend",
                "bench",
                "--site",
                site,
                "backup",
                "--with-files",
                "--compress",
            ],
        )
        if not context.dry_run:
            _compose(
                context,
                project,
                [
                    "cp",
                    f"backend:/home/frappe/frappe-bench/sites/{site}/private/backups/.",
                    str(backup_dir),
                ],
            )
        archive = backup_dir
    return {"project": project.name, "backup": str(archive), "created": not context.dry_run}


def restore_backup(
    context: RuntimeContext,
    project: ProjectConfig,
    *,
    archive: Path,
    target_identifier: str,
) -> dict[str, object]:
    resolved = archive.resolve()
    if not resolved.is_file():
        raise NoxusError(f"Restore archive does not exist: {resolved}", exit_code=ExitCode.USAGE)
    expected = project.site_name or (
        "noxus" if project.project_type is ProjectType.WEBSITE else f"{project.name}.localhost"
    )
    if target_identifier != expected:
        raise NoxusError(f"Restore target must exactly match {expected}", exit_code=ExitCode.UNSAFE)
    journal = OperationJournal(project.root)
    journal.record("restore", f"{expected}:{resolved}", "started")
    create_backup(context, project)
    try:
        if project.project_type is ProjectType.WEBSITE:
            if project.docker:
                sql = resolved.read_text(encoding="utf-8") if not context.dry_run else ""
                compose = _compose_file(project)
                ProcessRunner(context).run(
                    [
                        "docker",
                        "compose",
                        "--project-directory",
                        str(project.root),
                        "-f",
                        str(compose),
                        "exec",
                        "-T",
                        "db",
                        "psql",
                        "-v",
                        "ON_ERROR_STOP=1",
                        "-U",
                        "noxus",
                        "noxus",
                    ],
                    cwd=project.root,
                    stdin_text=sql,
                    timeout=900,
                )
            else:
                if resolved.suffix != ".sqlite3":
                    raise NoxusError(
                        "A local SQLite restore requires a .sqlite3 archive",
                        exit_code=ExitCode.USAGE,
                    )
                if not context.dry_run:
                    shutil.copy2(resolved, project.root / "db.sqlite3")
        else:
            site = project.site_name or f"{project.name}.localhost"
            _compose(
                context,
                project,
                [
                    "--profile",
                    "development",
                    "run",
                    "--rm",
                    "-T",
                    "-e",
                    f"NOXUS_SITE={site}",
                    "-e",
                    "NOXUS_BACKUP_PATH=/restore/input",
                    "-v",
                    f"{resolved}:/restore/input:ro",
                    "site-creator",
                    "bash",
                    "/opt/noxus/scripts/restore-site-entrypoint.sh",
                    "env/bin/python",
                    "/opt/noxus/scripts/restore_site.py",
                ],
            )
            _compose(
                context, project, ["exec", "-T", "backend", "bench", "--site", site, "migrate"]
            )
    except Exception as exc:
        journal.record("restore", f"{expected}:{resolved}", "failed", str(exc))
        raise
    journal.record("restore", f"{expected}:{resolved}", "complete")
    return {
        "project": project.name,
        "archive": str(resolved),
        "target": expected,
        "restored": not context.dry_run,
    }


def initialize_existing(
    context: RuntimeContext, bench: Path, *, site: str | None
) -> dict[str, object]:
    if not bench.is_dir() or not (bench / "sites").is_dir():
        raise NoxusError(f"Not a Frappe bench: {bench}", exit_code=ExitCode.USAGE)
    if not site:
        raise NoxusError(
            "--site is required for an existing Frappe bench", exit_code=ExitCode.USAGE
        )
    site_path = bench / "sites" / site
    if not site_path.is_dir():
        raise NoxusError(f"Frappe site does not exist: {site_path}", exit_code=ExitCode.USAGE)
    config = ProjectConfig(
        name=site.replace(".", "-").replace("_", "-")[:64],
        project_type=ProjectType.FRAPPE_EXISTING,
        database="mariadb",
        site_name=site,
        root=bench,
    )
    if not context.dry_run:
        write_project(config, bench)
    return {"bench": str(bench), "site": site, "initialized": not context.dry_run}


def install_modules(
    context: RuntimeContext,
    project: ProjectConfig,
    modules: list[str],
    *,
    site: str | None,
) -> None:
    target_site = site or project.site_name or f"{project.name}.localhost"
    journal = OperationJournal(project.root)
    for module in modules:
        journal.record("module-install", f"{target_site}:{module}", "started")
        if project.docker:
            _compose(
                context,
                project,
                ["exec", "backend", "bench", "--site", target_site, "install-app", module],
            )
        else:
            executable = shutil.which("bench")
            if not executable:
                raise NoxusError("bench is not available", exit_code=ExitCode.PREREQUISITE)
            ProcessRunner(context).run(
                [executable, "--site", target_site, "install-app", module], cwd=project.root
            )
        journal.record("module-install", f"{target_site}:{module}", "complete")


def uninstall_module(
    context: RuntimeContext,
    project: ProjectConfig,
    module: str,
    *,
    site: str,
) -> None:
    lifecycle_action(context, project, "backup")
    if project.docker:
        _compose(
            context,
            project,
            ["exec", "backend", "bench", "--site", site, "uninstall-app", module, "--yes"],
        )
    else:
        ProcessRunner(context).run(
            ["bench", "--site", site, "uninstall-app", module, "--yes"], cwd=project.root
        )
