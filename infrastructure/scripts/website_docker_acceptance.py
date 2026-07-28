"""Exercise a generated PostgreSQL website in disposable Docker resources."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = (
    "company,website,navigation,hero,about,services,portfolio,team,testimonials,faqs,"
    "blog,contact,newsletter,media,seo,social,legal,analytics,dashboard"
)


def run(args: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if check and completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed


def wait_for(url: str, timeout: int = 300) -> None:
    deadline = time.monotonic() + timeout
    last_error = "no response"
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(  # noqa: S310 - fixed loopback acceptance URL
                url
            )
            with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
                if response.status == 200:
                    return
                last_error = f"HTTP {response.status}"
        except (OSError, urllib.error.URLError) as exc:
            last_error = str(exc)
        time.sleep(2)
    raise RuntimeError(f"website did not become healthy: {last_error}")


def compose(
    project: Path, args: list[str], *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return run(
        ["docker", "compose", "--profile", "development", *args],
        cwd=project,
        check=check,
    )


def main() -> None:
    workspace = Path(tempfile.mkdtemp(prefix="noxus-website-acceptance-"))
    project = workspace / "acceptance-website"
    compose_attempted = False
    try:
        run(
            [
                sys.executable,
                "-m",
                "noxusai.main",
                "new",
                "website",
                "--name",
                "acceptance-website",
                "--directory",
                str(workspace),
                "--database",
                "postgres",
                "--auth",
                "both",
                "--language",
                "both",
                "--modules",
                MODULES,
                "--docker",
                "--no-start",
                "--yes",
            ],
            cwd=ROOT,
        )
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
        )
        compose_attempted = True
        compose(project, ["up", "--build", "--detach"])
        wait_for("http://127.0.0.1:8000/health/ready", timeout=600)
        wait_for("http://127.0.0.1:8000/api/schema/", timeout=120)
        compose(
            project,
            [
                "exec",
                "-T",
                "-e",
                "DJANGO_SETTINGS_MODULE=config.settings.test",
                "web",
                "/app/docker/entrypoint.sh",
                "python",
                "-m",
                "pytest",
                "-q",
            ],
        )

        run([sys.executable, "-m", "noxusai.main", "backup"], cwd=project)
        backups = sorted(
            (project / ".noxus" / "backups").rglob("database.sql"),
            key=lambda path: path.stat().st_mtime,
        )
        if not backups:
            raise RuntimeError("website backup was not created")
        run(
            [
                sys.executable,
                "-m",
                "noxusai.main",
                "restore",
                "--archive",
                str(backups[-1]),
                "--target",
                "noxus",
                "--yes",
                "--confirm-target",
                "noxus",
            ],
            cwd=project,
        )
        compose(project, ["restart", "web"])
        wait_for("http://127.0.0.1:8000/health/ready", timeout=300)
    except Exception:
        if compose_attempted:
            logs = compose(project, ["logs", "--no-color", "--tail", "500"], check=False)
            sys.stderr.write(logs.stdout + logs.stderr)
        raise
    finally:
        if compose_attempted:
            compose(project, ["down", "--volumes", "--remove-orphans"], check=False)
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    main()
