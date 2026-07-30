from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import stat
import uuid
from importlib.resources import files
from pathlib import Path
from typing import Literal

import yaml
from noxus_module_sdk.manifest import ModuleManifest
from noxus_module_sdk.project import ProjectConfig, ProjectType
from noxus_module_sdk.release import ReleaseManifest
from noxus_module_sdk.resolver import DependencyResolver, ResolutionError
from noxusai.context import RuntimeContext
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.configuration import write_project
from noxusai.services.process import ProcessRunner

SUPPORTED_MODULES = {
    "crm": "noxus_crm",
    "inventory": "noxus_inventory",
    "projects": "noxus_projects",
    "support": "noxus_support",
    "maintenance": "noxus_maintenance",
    "transport": "noxus_transport",
    "education": "noxus_education",
    "ai": "noxus_ai",
}
INDUSTRIES = {
    "general-business",
    "transportation",
    "education",
    "maintenance",
    "hotel-operations",
    "professional-services",
    "empty",
}


def _resolve_apps(payload: Path, requested: list[str], *, with_erpnext: bool) -> list[str]:
    manifests: list[ModuleManifest] = []
    for path in sorted((payload / "frappe_apps").glob("noxus_*/noxus-module.yml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        manifests.append(ModuleManifest.model_validate(raw))
    if not manifests:
        raise NoxusError("SaaS payload contains no module manifests", exit_code=ExitCode.UNSAFE)
    try:
        resolution = DependencyResolver(
            manifests,
            erpnext_version="16.29.0" if with_erpnext else None,
        ).resolve(requested)
    except ResolutionError as exc:
        raise NoxusError(f"Module resolution failed: {exc}", exit_code=ExitCode.CONFLICT) from exc
    return [item.name for item in resolution.installation_order]


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _payload_root() -> Path:
    packaged = Path(str(files("noxusai").joinpath("payload")))
    if packaged.is_dir():
        return packaged
    root = _repository_root()
    if (root / "frappe_apps").is_dir() and (root / "infrastructure").is_dir():
        return root
    raise NoxusError("The installed wheel does not contain the NOXUS runtime payload")


def _verify_manifest(payload: Path) -> ReleaseManifest | None:
    manifest_path = payload / "release-manifest.json"
    if not manifest_path.is_file():
        if (payload / "pyproject.toml").is_file():
            return None
        raise NoxusError("Bundled release manifest is missing", exit_code=ExitCode.UNSAFE)
    manifest = ReleaseManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.files:
        candidate = (payload / entry.path).resolve()
        if payload.resolve() not in candidate.parents or not candidate.is_file():
            raise NoxusError(
                f"Release payload file is missing: {entry.path}", exit_code=ExitCode.UNSAFE
            )
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != entry.sha256 or candidate.stat().st_size != entry.size:
            raise NoxusError(
                f"Release payload checksum failed: {entry.path}", exit_code=ExitCode.UNSAFE
            )
    return manifest


def _check_secret_file(path: Path | None) -> Path | None:
    if path is None:
        return None
    resolved = path.resolve()
    if not resolved.is_file():
        raise NoxusError(
            f"Administrator secret file does not exist: {resolved}", exit_code=ExitCode.USAGE
        )
    if os.name != "nt" and stat.S_IMODE(resolved.stat().st_mode) & 0o077:
        raise NoxusError(
            "Administrator secret file must not be accessible by group or other users",
            exit_code=ExitCode.PERMISSION,
        )
    if not resolved.read_text(encoding="utf-8").strip():
        raise NoxusError("Administrator secret file is empty", exit_code=ExitCode.USAGE)
    return resolved


def _copy_bundled_payload(payload: Path, staging: Path) -> None:
    for name in ("frappe_apps", "infrastructure", "docs"):
        source = payload / name
        if not source.is_dir():
            raise NoxusError(f"Bundled payload is missing {name}", exit_code=ExitCode.UNSAFE)
        shutil.copytree(source, staging / name)
    ui_source = payload / "ui" / "dist"
    if not ui_source.is_dir():
        raise NoxusError("Bundled payload is missing compiled UI assets", exit_code=ExitCode.UNSAFE)
    shutil.copytree(ui_source, staging / "ui" / "dist")
    license_source = payload / "LICENSE"
    if not license_source.is_file():
        raise NoxusError("Bundled payload is missing its license", exit_code=ExitCode.UNSAFE)
    shutil.copy2(license_source, staging / "LICENSE")
    manifest_source = payload / "release-manifest.json"
    if manifest_source.is_file():
        shutil.copy2(manifest_source, staging / "release-manifest.json")


def generate_saas(
    context: RuntimeContext,
    *,
    target: Path,
    name: str,
    industry: str,
    language: Literal["english", "arabic", "both"],
    modules: list[str],
    with_erpnext: bool,
    edge_repository: str | None,
    edge_branch: str | None,
    admin_secret_file: Path | None,
    docker: bool,
    start: bool,
) -> dict[str, object]:
    if not docker:
        raise NoxusError("SaaS projects require Docker", exit_code=ExitCode.USAGE)
    if industry not in INDUSTRIES:
        raise NoxusError(f"Unknown industry: {industry}", exit_code=ExitCode.USAGE)
    unknown = sorted(set(modules) - SUPPORTED_MODULES.keys())
    if unknown:
        raise NoxusError(f"Unknown SaaS modules: {', '.join(unknown)}", exit_code=ExitCode.USAGE)
    requested = ["noxus_core", *sorted({SUPPORTED_MODULES[item] for item in modules})]
    if target.exists():
        raise NoxusError(f"Target already exists: {target}", exit_code=ExitCode.CONFLICT)
    secret_file = _check_secret_file(admin_secret_file)
    if context.dry_run:
        selected = _resolve_apps(_payload_root(), requested, with_erpnext=with_erpnext)
        return {"project": name, "target": str(target), "apps": selected, "created": False}

    staging = target.parent / f".{target.name}.noxus-tmp-{uuid.uuid4().hex[:8]}"
    runner = ProcessRunner(context)
    try:
        staging.mkdir(parents=True)
        release: ReleaseManifest | None = None
        if edge_repository:
            if not edge_branch:
                raise NoxusError(
                    "Edge source requires an explicit branch", exit_code=ExitCode.USAGE
                )
            shutil.rmtree(staging)
            runner.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    edge_branch,
                    "--single-branch",
                    edge_repository,
                    str(staging),
                ],
                cwd=target.parent,
                timeout=300,
            )
        else:
            payload = _payload_root()
            release = _verify_manifest(payload)
            _copy_bundled_payload(payload, staging)

        selected = _resolve_apps(staging, requested, with_erpnext=with_erpnext)

        compose_source = staging / "infrastructure" / "docker" / "compose.yaml"
        if not compose_source.is_file():
            raise NoxusError("SaaS payload has no Compose definition", exit_code=ExitCode.UNSAFE)
        compose_text = compose_source.read_text(encoding="utf-8").replace(
            "context: ../..", "context: ."
        )
        (staging / "compose.yaml").write_text(compose_text, encoding="utf-8")
        production_source = staging / "infrastructure" / "docker" / "compose.production.yaml"
        if not production_source.is_file():
            raise NoxusError(
                "SaaS payload has no production Compose override", exit_code=ExitCode.UNSAFE
            )
        (staging / "compose.production.yaml").write_text(
            production_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
        environment = [
            f"COMPOSE_PROJECT_NAME={name}",
            f"NOXUS_SITE={name}.localhost",
            f"NOXUS_LANGUAGE={language}",
            f"NOXUS_APPS={','.join(selected)}",
            f"NOXUS_WITH_ERPNEXT={'1' if with_erpnext else '0'}",
            "NOXUS_HTTP_PORT=8080",
        ]
        if secret_file:
            environment.append(f"NOXUS_ADMIN_PASSWORD_FILE={secret_file}")
        secret_directory = staging / "secrets"
        secret_directory.mkdir()
        (secret_directory / "mariadb_root_password.txt").write_text(
            secrets.token_urlsafe(36) + "\n", encoding="utf-8"
        )
        (secret_directory / "admin_password.txt").write_text("", encoding="utf-8")
        (staging / ".gitignore").write_text(
            ".env\nsecrets/*.txt\n!secrets/.gitkeep\n", encoding="utf-8"
        )
        (secret_directory / ".gitkeep").write_text("", encoding="utf-8")
        (staging / ".env").write_text("\n".join(environment) + "\n", encoding="utf-8")
        (staging / ".env.example").write_text(
            "NOXUS_SITE=example.localhost\nNOXUS_ADMIN_PASSWORD_FILE=/absolute/protected/admin-password.txt\nNOXUS_HTTP_PORT=8080\n",
            encoding="utf-8",
        )
        config = ProjectConfig(
            name=name,
            project_type=ProjectType.SAAS,
            language=language,
            database="mariadb",
            authentication="session",
            docker=True,
            site_name=f"{name}.localhost",
            modules=selected,
            with_erpnext=with_erpnext,
            root=staging,
        )
        write_project(config, staging)
        (staging / ".noxus" / "payload.json").write_text(
            json.dumps(
                {
                    "version": release.noxus_version if release else "source-development",
                    "verified": release is not None,
                    "apps": selected,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        staging.rename(target)
    except Exception:
        if (
            staging.exists()
            and staging.parent == target.parent
            and staging.name.startswith(f".{target.name}.noxus-tmp-")
        ):
            shutil.rmtree(staging)
        raise

    if start:
        if not secret_file and not os.environ.get("NOXUS_ADMIN_PASSWORD"):
            raise NoxusError(
                "Starting site creation requires --admin-secret-file or NOXUS_ADMIN_PASSWORD",
                exit_code=ExitCode.USAGE,
            )
        runner.run(
            ["docker", "compose", "--profile", "development", "up", "--build", "--detach"],
            cwd=target,
            timeout=1800,
        )
    return {
        "project": name,
        "target": str(target),
        "site": f"{name}.localhost",
        "apps": selected,
        "erpnext": with_erpnext,
        "created": True,
        "started": start,
        "url": "http://localhost:8080/noxus",
    }
