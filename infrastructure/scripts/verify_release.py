from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

from noxus_module_sdk.release import ReleaseManifest

ROOT = Path(__file__).resolve().parents[2]


def run(args: list[str], cwd: Path = ROOT) -> None:
    completed = subprocess.run(args, cwd=cwd, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def command(name: str) -> str:
    candidates = [f"{name}.cmd", name] if sys.platform == "win32" else [name]
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise SystemExit(f"required release tool is unavailable: {name}")


def verify_payload() -> None:
    manifest = ReleaseManifest.model_validate_json(
        (ROOT / "release-manifest.json").read_text(encoding="utf-8")
    )
    for entry in manifest.files:
        path = (ROOT / entry.path).resolve()
        if ROOT.resolve() not in path.parents and path != ROOT.resolve():
            raise SystemExit(f"unsafe manifest path: {entry.path}")
        if (
            not path.is_file()
            or path.stat().st_size != entry.size
            or hashlib.sha256(path.read_bytes()).hexdigest() != entry.sha256
        ):
            raise SystemExit(f"payload verification failed: {entry.path}")


def clean_wheel_smoke_test() -> None:
    wheels = sorted((ROOT / "dist").glob("noxusai-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("release check requires exactly one NOXUS wheel in dist")
    with tempfile.TemporaryDirectory(prefix="noxus-wheel-check-") as temporary:
        workspace = Path(temporary)
        environment = workspace / ".venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        run([str(python), "-m", "pip", "install", "--quiet", str(wheels[0])], cwd=workspace)
        run([str(python), "-m", "noxusai.main", "--version"], cwd=workspace)
        run(
            [str(python), "-m", "noxusai.main", "--json", "doctor", "--workflow", "website"],
            cwd=workspace,
        )
        projects = workspace / "projects"
        projects.mkdir()
        run(
            [
                str(python),
                "-m",
                "noxusai.main",
                "new",
                "website",
                "--name",
                "release-website",
                "--directory",
                str(projects),
                "--database",
                "sqlite",
                "--modules",
                "company,website,contact,seo",
                "--no-docker",
                "--yes",
            ],
            cwd=workspace,
        )
        website = projects / "release-website"
        run(
            [str(python), "-m", "pip", "install", "--quiet", "-r", "requirements.txt"],
            cwd=website,
        )
        run([str(python), "manage.py", "migrate", "--noinput"], cwd=website)
        run([str(python), "-m", "pytest", "-q"], cwd=website)
        run(
            [
                str(python),
                "-m",
                "noxusai.main",
                "new",
                "saas",
                "--name",
                "release-saas",
                "--directory",
                str(projects),
                "--modules",
                "crm,inventory",
                "--without-erpnext",
                "--docker",
                "--no-start",
                "--yes",
            ],
            cwd=workspace,
        )
        generated_manifest = projects / "release-saas" / "release-manifest.json"
        if generated_manifest.read_bytes() != (ROOT / "release-manifest.json").read_bytes():
            raise SystemExit("wheel contains a stale release payload manifest")
        run([str(python), "-m", "pip", "check"], cwd=workspace)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--containers",
        action="store_true",
        help="Run destructive disposable website, Frappe, and ERPNext container acceptance.",
    )
    args = parser.parse_args()

    verify_payload()
    run([sys.executable, "-m", "ruff", "check", "."])
    run([sys.executable, "-m", "ruff", "format", "--check", "."])
    run([sys.executable, "-m", "mypy"])
    run([sys.executable, "-m", "pytest", "-q"])
    run([command("npm"), "run", "lint"])
    run([command("npm"), "run", "typecheck"])
    run([command("npm"), "test"])
    run([command("npm"), "run", "build"])
    # Vite asset names are content-addressed. Recheck after the build so a stale
    # committed manifest fails before a wheel can be assembled.
    verify_payload()
    run([command("npm"), "run", "test:e2e"])
    run([sys.executable, "-m", "pip_audit", "-r", "requirements-cli.lock"])
    run(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "-r",
            "cli/noxusai/templates/website/requirements.txt.j2",
        ]
    )
    run([command("npm"), "audit", "--audit-level=critical"])
    shutil.rmtree(ROOT / "dist", ignore_errors=True)
    run([sys.executable, "-m", "build"])
    run([sys.executable, "-m", "twine", "check", "dist/*"])
    clean_wheel_smoke_test()
    if args.containers:
        run([sys.executable, "infrastructure/scripts/website_docker_acceptance.py"])
        run([sys.executable, "infrastructure/scripts/docker_acceptance.py"])
        run([sys.executable, "infrastructure/scripts/docker_acceptance.py", "--with-erpnext"])


if __name__ == "__main__":
    main()
