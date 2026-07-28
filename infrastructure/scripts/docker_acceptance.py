"""Run the destructive container acceptance suite in an isolated temporary project."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALL_MODULES = "crm,inventory,projects,support,maintenance,transport,education,ai"


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
    project: Path, args: list[str], *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return run(
        ["docker", "compose", "--profile", "development", *args],
        cwd=project,
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
        apps_result = compose(
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
        installed = json.loads(apps_result.stdout)
        expected = {"frappe", "noxus_core", *(f"noxus_{name}" for name in ALL_MODULES.split(","))}
        if args.with_erpnext:
            expected.add("erpnext")
        missing = expected - set(installed.get(site, []))
        if missing:
            raise RuntimeError(f"installed app set is incomplete: {sorted(missing)}")

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
