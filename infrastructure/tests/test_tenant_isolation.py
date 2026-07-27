import os
import subprocess
from pathlib import Path

import pytest


def run(args: list[str], *, cwd: Path, environment: dict[str, str] | None = None) -> str:
    process_environment = os.environ.copy()
    if environment:
        process_environment.update(environment)
    completed = subprocess.run(
        args,
        cwd=cwd,
        env=process_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return completed.stdout


@pytest.mark.docker
@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("NOXUS_RUN_DOCKER_ACCEPTANCE") != "1", reason="set NOXUS_RUN_DOCKER_ACCEPTANCE=1"
)
def test_two_real_sites_keep_identical_ids_isolated() -> None:
    configured_project = os.getenv("NOXUS_DOCKER_PROJECT", "")
    assert configured_project, "NOXUS_DOCKER_PROJECT must name a disposable generated SaaS project"
    project = Path(configured_project).resolve()
    assert (project / "compose.yaml").is_file()
    test_password = os.getenv("NOXUS_TEST_ADMIN_PASSWORD", "")
    assert test_password, (
        "NOXUS_TEST_ADMIN_PASSWORD must be supplied through the protected environment"
    )

    compose = ["docker", "compose", "--profile", "development"]
    run([*compose, "up", "--build", "--detach"], cwd=project)
    site_a, site_b = "tenant-a.localhost", "tenant-b.localhost"
    for site in (site_a, site_b):
        run(
            [
                *compose,
                "run",
                "--rm",
                "-T",
                "-e",
                "NOXUS_ADMIN_PASSWORD",
                "-e",
                f"NOXUS_SITE={site}",
                "-e",
                "NOXUS_APPS=noxus_core",
                "site-creator",
            ],
            cwd=project,
            environment={"NOXUS_ADMIN_PASSWORD": test_password},
        )
        run(
            [
                *compose,
                "exec",
                "-T",
                "backend",
                "bench",
                "--site",
                site,
                "execute",
                "noxus_core.tests.isolation.create_marker",
            ],
            cwd=project,
        )
    for site in (site_a, site_b):
        output = run(
            [
                *compose,
                "exec",
                "-T",
                "backend",
                "bench",
                "--site",
                site,
                "execute",
                "noxus_core.tests.isolation.get_marker",
            ],
            cwd=project,
        )
        assert site in output
