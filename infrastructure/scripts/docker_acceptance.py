"""Run the destructive container acceptance suite in an isolated temporary project."""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALL_MODULES = "crm,inventory,projects,support,maintenance,transport,education,ai"
INDEPENDENT_APP_SETS = {
    "crm": ["noxus_core", "noxus_crm"],
    "inventory": ["noxus_core", "noxus_inventory"],
    "projects": ["noxus_core", "noxus_projects"],
    "support": ["noxus_core", "noxus_support"],
    "maintenance": ["noxus_core", "noxus_inventory", "noxus_maintenance"],
    "transport": ["noxus_core", "noxus_transport"],
    "education": ["noxus_core", "noxus_education"],
    "ai": ["noxus_core", "noxus_ai"],
}


def run(
    args: list[str],
    *,
    cwd: Path,
    environment: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=process_environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=3600,
    )
    if check and completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed


def wait_for_health(url: str, timeout: int = 300, *, host: str | None = None) -> None:
    deadline = time.monotonic() + timeout
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(  # noqa: S310 - fixed loopback acceptance URLs only
                url, headers={"Host": host} if host else {}
            )
            with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
                if response.status == 200:
                    return
                last_error = f"HTTP {response.status}"
        except (OSError, urllib.error.URLError) as exc:
            last_error = str(exc)
        time.sleep(3)
    raise RuntimeError(f"health endpoint did not become ready: {last_error}")


def compose(
    project: Path,
    args: list[str],
    *,
    environment: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return run(
        ["docker", "compose", "--profile", "development", *args],
        cwd=project,
        environment=environment,
        check=check,
    )


def newest_database_backup(project: Path) -> Path:
    candidates = sorted(
        (project / ".noxus" / "backups").rglob("*.sql.gz"),
        key=lambda path: path.stat().st_mtime,
    )
    if not candidates:
        raise RuntimeError("Frappe backup did not produce a compressed database archive")
    return candidates[-1]


def response_data(payload: dict[str, object]) -> object:
    if "data" in payload:
        return payload["data"]
    if "message" in payload:
        return payload["message"]
    raise RuntimeError(f"Frappe response did not use a supported envelope: {sorted(payload)}")


def api_request(
    opener: urllib.request.OpenerDirector,
    site: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
    csrf_token: str = "",
) -> dict[str, object]:
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Host": site, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
        if csrf_token:
            headers["X-Frappe-CSRF-Token"] = csrf_token
    request = urllib.request.Request(f"http://127.0.0.1:8080{path}", data=body, headers=headers)
    with opener.open(request, timeout=30) as response:
        decoded = json.loads(response.read())
    if not isinstance(decoded, dict):
        raise RuntimeError("Frappe returned a non-object JSON response")
    return decoded


def exercise_live_api_contract(site: str, admin_password: str) -> None:
    catalog_path = "/api/v2/method/noxus_core.api.v1.catalog"
    try:
        api_request(urllib.request.build_opener(), site, catalog_path)
    except urllib.error.HTTPError as exc:
        if exc.code not in {401, 403, 417}:
            raise RuntimeError(f"unexpected unauthenticated catalog status: {exc.code}") from exc
    else:
        raise RuntimeError("the protected module catalog allowed an unauthenticated request")

    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    login = api_request(
        opener,
        site,
        "/api/method/login",
        payload={"usr": "Administrator", "pwd": admin_password},
    )
    if not response_data(login):
        raise RuntimeError("Frappe login did not return a successful response")
    csrf_token = next(
        (urllib.parse.unquote(cookie.value) for cookie in cookies if cookie.name == "csrf_token"),
        "",
    )

    catalog = response_data(api_request(opener, site, catalog_path))
    if not isinstance(catalog, dict):
        raise RuntimeError("catalog response is not an object")
    modules = catalog.get("modules")
    names = (
        {item.get("name") for item in modules if isinstance(item, dict)}
        if isinstance(modules, list)
        else set()
    )
    if "noxus_core" not in names:
        raise RuntimeError("authenticated catalog did not include noxus_core")
    marketplace = catalog.get("remote_marketplace")
    if not isinstance(marketplace, dict) or marketplace.get("available") is not False:
        raise RuntimeError("remote marketplace must remain visibly unavailable in Community v1")

    resolved = response_data(
        api_request(
            opener,
            site,
            "/api/v2/method/noxus_core.api.v1.resolve_modules",
            payload={
                "request": {
                    "modules": ["noxus_maintenance"],
                    "platform": {"python": "3.14.6", "frappe": "16.28.0"},
                }
            },
            csrf_token=csrf_token,
        )
    )
    expected_order = ["noxus_core", "noxus_inventory", "noxus_maintenance"]
    if not isinstance(resolved, dict) or resolved.get("install_order") != expected_order:
        raise RuntimeError(f"live dependency resolution returned an unexpected result: {resolved}")


def installed_apps(project: Path, site: str) -> set[str]:
    result = compose(
        project,
        [
            "exec",
            "-T",
            "backend",
            "bench",
            "--site",
            site,
            "list-apps",
            "--format",
            "json",
        ],
    )
    decoded = json.loads(result.stdout)
    return set(decoded.get(site, []))


def exercise_independent_installs(project: Path, admin_password: str) -> None:
    for label, apps in INDEPENDENT_APP_SETS.items():
        site = f"independent-{label}.localhost"
        compose(
            project,
            [
                "run",
                "--rm",
                "-T",
                "-e",
                "NOXUS_ADMIN_PASSWORD",
                "-e",
                f"NOXUS_SITE={site}",
                "-e",
                f"NOXUS_APPS={','.join(apps)}",
                "-e",
                "NOXUS_WITH_ERPNEXT=0",
                "site-creator",
            ],
            environment={"NOXUS_ADMIN_PASSWORD": admin_password},
        )
        missing = set(apps) - installed_apps(project, site)
        if missing:
            raise RuntimeError(f"{label} independent install is incomplete: {sorted(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-erpnext", action="store_true")
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()

    workspace = Path(tempfile.mkdtemp(prefix="noxus-container-acceptance-"))
    project_name = "acceptance-erpnext" if args.with_erpnext else "acceptance-frappe"
    project = workspace / project_name
    admin_secret = workspace / "admin-password.txt"
    admin_password = secrets.token_urlsafe(32)
    admin_secret.write_text(admin_password + "\n", encoding="utf-8")
    admin_secret.chmod(0o600)
    generate = [
        sys.executable,
        "-m",
        "noxusai.main",
        "new",
        "saas",
        "--name",
        project_name,
        "--directory",
        str(workspace),
        "--industry",
        "maintenance",
        "--modules",
        ALL_MODULES,
        "--admin-secret-file",
        str(admin_secret),
        "--docker",
        "--no-start",
        "--yes",
        "--with-erpnext" if args.with_erpnext else "--without-erpnext",
    ]

    compose_started = False
    try:
        run(generate, cwd=ROOT)
        compose(project, ["config", "--quiet"])
        run(
            [
                "docker",
                "compose",
                "-f",
                "compose.yaml",
                "-f",
                "compose.production.yaml",
                "--profile",
                "production",
                "config",
                "--quiet",
            ],
            cwd=project,
            environment={"NOXUS_DEPLOYMENT_PROFILE": "production"},
        )
        compose_started = True
        compose(project, ["up", "--build", "--detach"])
        wait_for_health("http://127.0.0.1:8080/healthz", timeout=600)
        site = f"{project_name}.localhost"
        wait_for_health(
            "http://127.0.0.1:8080/api/v2/method/noxus_core.api.v1.health",
            timeout=120,
            host=site,
        )
        expected = {"frappe", "noxus_core", *(f"noxus_{name}" for name in ALL_MODULES.split(","))}
        if args.with_erpnext:
            expected.add("erpnext")
        missing = expected - installed_apps(project, site)
        if missing:
            raise RuntimeError(f"installed app set is incomplete: {sorted(missing)}")

        exercise_live_api_contract(site, admin_password)

        compose(
            project,
            [
                "exec",
                "-T",
                "backend",
                "bench",
                "--site",
                site,
                "run-tests",
                "--app",
                "noxus_core",
            ],
        )
        run(
            [sys.executable, "-m", "pytest", "infrastructure/tests", "-m", "docker", "-q"],
            cwd=project,
            environment={
                "NOXUS_RUN_DOCKER_ACCEPTANCE": "1",
                "NOXUS_DOCKER_PROJECT": str(project),
                "NOXUS_TEST_ADMIN_PASSWORD": admin_password,
            },
        )
        if not args.with_erpnext:
            exercise_independent_installs(project, admin_password)

        run([sys.executable, "-m", "noxusai.main", "backup"], cwd=project)
        archive = newest_database_backup(project)
        run(
            [
                sys.executable,
                "-m",
                "noxusai.main",
                "restore",
                "--archive",
                str(archive),
                "--target",
                site,
                "--yes",
                "--confirm-target",
                site,
            ],
            cwd=project,
        )
        compose(project, ["restart", "backend", "worker-short", "worker-long", "scheduler"])
        wait_for_health("http://127.0.0.1:8080/healthz", timeout=300)
    except Exception:
        if compose_started:
            logs = compose(project, ["logs", "--no-color", "--tail", "500"], check=False)
            sys.stderr.write(logs.stdout + logs.stderr)
        raise
    finally:
        if compose_started:
            compose(project, ["down", "--volumes", "--remove-orphans"], check=False)
        if args.keep:
            print(f"Acceptance workspace retained at {workspace}")
        else:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    main()
