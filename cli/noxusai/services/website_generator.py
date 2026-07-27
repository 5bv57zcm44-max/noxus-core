from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import uuid
from pathlib import Path
from typing import Literal

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from noxus_module_sdk.project import ProjectConfig, ProjectType
from noxusai.context import RuntimeContext
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import write_project
from noxusai.services.process import ProcessRunner

MODULES = {
    "company": "Company Profile",
    "website": "Website Settings",
    "navigation": "Navigation Menus",
    "hero": "Hero Sections",
    "about": "About Page",
    "services": "Services",
    "portfolio": "Portfolio",
    "team": "Team Members",
    "testimonials": "Testimonials",
    "faqs": "FAQs",
    "blog": "Blog",
    "contact": "Contact Messages",
    "newsletter": "Newsletter Subscriptions",
    "media": "Media Library",
    "seo": "SEO Metadata",
    "social": "Social Links",
    "legal": "Legal Pages",
    "analytics": "Analytics Events",
    "dashboard": "Admin Dashboard",
}
SPECIAL_MODULES = {"contact", "newsletter", "analytics", "media"}


def _class_name(module: str) -> str:
    return "".join(item.capitalize() for item in module.split("_")) + "Record"


def _template_root() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "website"


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(_template_root()),
        undefined=StrictUndefined,
        autoescape=False,  # noqa: S701 - templates generate source/config, never HTML responses
        keep_trailing_newline=True,
        variable_start_string="[[",
        variable_end_string="]]",
    )


def _render(environment: Environment, template: str, **context: object) -> str:
    return environment.get_template(template).render(**context)


def _safe_write(root: Path, relative: str, content: str, hashes: dict[str, str]) -> None:
    target = (root / relative).resolve()
    if root.resolve() not in target.parents:
        raise NoxusError(
            f"Template path escapes project root: {relative}", exit_code=ExitCode.UNSAFE
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
    hashes[relative] = hashlib.sha256(content.encode()).hexdigest()


def generate_website(
    context: RuntimeContext,
    *,
    target: Path,
    name: str,
    database: Literal["postgres", "sqlite", "mariadb"],
    authentication: Literal["jwt", "session", "both"],
    language: Literal["english", "arabic", "both"],
    modules: list[str],
    docker: bool,
    initialize_git: bool,
    start: bool,
) -> dict[str, object]:
    if database not in {"postgres", "sqlite"}:
        raise NoxusError("Website database must be postgres or sqlite", exit_code=ExitCode.USAGE)
    if docker and database != "postgres":
        raise NoxusError("Docker website projects require PostgreSQL", exit_code=ExitCode.USAGE)
    if authentication not in {"jwt", "session", "both"}:
        raise NoxusError("Authentication must be jwt, session, or both", exit_code=ExitCode.USAGE)
    if language not in {"english", "arabic", "both"}:
        raise NoxusError("Language must be english, arabic, or both", exit_code=ExitCode.USAGE)
    unknown = sorted(set(modules) - MODULES.keys())
    if unknown:
        raise NoxusError(f"Unknown website modules: {', '.join(unknown)}", exit_code=ExitCode.USAGE)
    selected = sorted(set(modules))
    if target.exists():
        raise NoxusError(f"Target already exists: {target}", exit_code=ExitCode.CONFLICT)
    if context.dry_run:
        return {"project": name, "target": str(target), "modules": selected, "created": False}

    staging = target.parent / f".{target.name}.noxus-tmp-{uuid.uuid4().hex[:8]}"
    if staging.exists() or staging.parent != target.parent:
        raise NoxusError("Unsafe staging destination", exit_code=ExitCode.UNSAFE)
    environment = _environment()
    hashes: dict[str, str] = {}
    common = {
        "project_name": name,
        "python_package": name.replace("-", "_"),
        "database": database,
        "authentication": authentication,
        "language": language,
        "modules": selected,
        "module_apps": [f"apps.{module}" for module in selected],
    }
    try:
        staging.mkdir(parents=True)
        static_templates = {
            "manage.py": "manage.py.j2",
            "requirements.txt": "requirements.txt.j2",
            "pytest.ini": "pytest.ini.j2",
            ".env.example": "env.example.j2",
            ".gitignore": "gitignore.j2",
            "LICENSE": "license.j2",
            "README.md": "readme.md.j2",
            "config/__init__.py": "empty.j2",
            "config/asgi.py": "config/asgi.py.j2",
            "config/wsgi.py": "config/wsgi.py.j2",
            "config/urls.py": "config/urls.py.j2",
            "config/settings/__init__.py": "empty.j2",
            "config/settings/base.py": "config/settings/base.py.j2",
            "config/settings/development.py": "config/settings/development.py.j2",
            "config/settings/test.py": "config/settings/test.py.j2",
            "config/settings/production.py": "config/settings/production.py.j2",
            "apps/__init__.py": "empty.j2",
            "apps/core/__init__.py": "empty.j2",
            "apps/core/apps.py": "core/apps.py.j2",
            "apps/core/models.py": "core/models.py.j2",
            "apps/core/views.py": "core/views.py.j2",
            "apps/core/urls.py": "core/urls.py.j2",
            "apps/core/admin.py": "empty.j2",
            "apps/core/management/__init__.py": "empty.j2",
            "apps/core/management/commands/__init__.py": "empty.j2",
            "apps/core/management/commands/seed.py": "core/seed.py.j2",
            "apps/core/tests/__init__.py": "empty.j2",
            "apps/core/tests/test_health.py": "core/test_health.py.j2",
            "apps/accounts/__init__.py": "empty.j2",
            "apps/accounts/apps.py": "accounts/apps.py.j2",
            "apps/accounts/models.py": "accounts/models.py.j2",
            "apps/accounts/admin.py": "accounts/admin.py.j2",
            "apps/accounts/migrations/__init__.py": "empty.j2",
            "apps/accounts/migrations/0001_initial.py": "accounts/migration.py.j2",
            "apps/accounts/tests/__init__.py": "empty.j2",
            "apps/accounts/tests/test_user.py": "accounts/test_user.py.j2",
        }
        if docker:
            static_templates.update(
                {
                    "Dockerfile": "docker/Dockerfile.j2",
                    "compose.yaml": "docker/compose.yaml.j2",
                    "compose.production.yaml": "docker/compose.production.yaml.j2",
                    "docker/entrypoint.sh": "docker/entrypoint.sh.j2",
                }
            )
        for relative, template in static_templates.items():
            _safe_write(staging, relative, _render(environment, template, **common), hashes)

        if docker:
            secret_directory = staging / "secrets"
            secret_directory.mkdir()
            secret_values = {
                "postgres_password.txt": secrets.token_urlsafe(36),
                "django_secret.txt": secrets.token_urlsafe(64),
            }
            for filename, value in secret_values.items():
                secret_path = secret_directory / filename
                secret_path.write_text(value + "\n", encoding="utf-8", newline="\n")
                if os.name != "nt":
                    secret_path.chmod(0o600)
            _safe_write(staging, "secrets/.gitkeep", "", hashes)

        for module in selected:
            module_context = {
                **common,
                "module": module,
                "display_name": MODULES[module],
                "class_name": _class_name(module),
            }
            template_set = "modules/special" if module in SPECIAL_MODULES else "modules/generic"
            for filename in (
                "apps.py",
                "models.py",
                "serializers.py",
                "views.py",
                "urls.py",
                "admin.py",
            ):
                _safe_write(
                    staging,
                    f"apps/{module}/{filename}",
                    _render(environment, f"{template_set}/{filename}.j2", **module_context),
                    hashes,
                )
            _safe_write(staging, f"apps/{module}/__init__.py", "", hashes)
            _safe_write(staging, f"apps/{module}/migrations/__init__.py", "", hashes)
            _safe_write(
                staging,
                f"apps/{module}/migrations/0001_initial.py",
                _render(environment, f"{template_set}/migration.py.j2", **module_context),
                hashes,
            )
            _safe_write(staging, f"apps/{module}/tests/__init__.py", "", hashes)
            _safe_write(
                staging,
                f"apps/{module}/tests/test_api.py",
                _render(environment, f"{template_set}/test_api.py.j2", **module_context),
                hashes,
            )

        config = ProjectConfig(
            name=name,
            project_type=ProjectType.WEBSITE,
            environment="development",
            language=language,
            database=database,
            authentication=authentication,
            docker=docker,
            modules=selected,
            root=staging,
        )
        write_project(config, staging)
        lock = {"template_version": "1.0.0rc1", "files": dict(sorted(hashes.items()))}
        _safe_write(staging, ".noxus/template-lock.json", json.dumps(lock, indent=2) + "\n", hashes)
        staging.rename(target)
    except Exception:
        if (
            staging.exists()
            and staging.parent == target.parent
            and staging.name.startswith(f".{target.name}.noxus-tmp-")
        ):
            shutil.rmtree(staging)
        raise

    runner = ProcessRunner(context)
    if initialize_git:
        runner.run(["git", "init"], cwd=target)
    if start:
        if docker:
            runner.run(
                [
                    "docker",
                    "compose",
                    "--profile",
                    "development",
                    "up",
                    "--build",
                    "--detach",
                ],
                cwd=target,
                timeout=900,
            )
        else:
            runner.run(["python", "manage.py", "runserver"], cwd=target, timeout=86400)
    return {
        "project": name,
        "target": str(target),
        "modules": selected,
        "created": True,
        "next": f"cd {target.name} && copy .env.example .env && docker compose up --build"
        if docker
        else f"cd {target.name} && python manage.py migrate",
    }
