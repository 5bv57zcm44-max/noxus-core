from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

from typer.testing import CliRunner

from noxusai.main import app
from noxusai.services.doctor import _command_check

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "1.0.0"


def test_doctor_json_has_stable_envelope() -> None:
    result = runner.invoke(app, ["--json", "doctor", "--workflow", "website"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["command"] == "doctor"
    assert any(check["name"] == "Python" for check in payload["data"])


def test_new_website_requires_name_in_json_mode() -> None:
    result = runner.invoke(app, ["--json", "new", "website", "--yes"])
    assert result.exit_code != 0


def test_interactive_saas_name_reprompts_without_a_traceback() -> None:
    result = runner.invoke(
        app,
        ["--dry-run", "new", "saas"],
        input="invalid_name\nauraco-business\n",
    )
    assert result.exit_code == 0
    assert "Invalid project name" in result.stdout
    assert "auraco-business" in result.stdout
    assert "Traceback" not in result.stdout


def test_invalid_noninteractive_name_is_a_concise_usage_error(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "noxusai.main",
            "new",
            "saas",
            "--name",
            "invalid_name",
            "--directory",
            str(tmp_path),
            "--yes",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert "Error: Use 3-64 lowercase letters, numbers, and hyphens" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_invalid_json_name_uses_the_stable_error_envelope(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "noxusai.main",
            "--json",
            "new",
            "website",
            "--name",
            "invalid_name",
            "--directory",
            str(tmp_path),
            "--yes",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stderr)
    assert completed.returncode == 2
    assert payload == {
        "ok": False,
        "command": None,
        "data": None,
        "warnings": [],
        "error": {
            "message": "Use 3-64 lowercase letters, numbers, and hyphens",
            "code": 2,
        },
    }


def test_optional_doctor_command_timeout_becomes_a_warning(monkeypatch) -> None:
    monkeypatch.setattr("noxusai.services.doctor.shutil.which", lambda _command: "docker")
    process_runner = MagicMock()
    process_runner.run.side_effect = subprocess.TimeoutExpired(("docker", "compose"), 15)

    check = _command_check(
        process_runner, "Docker Compose", ["docker", "compose", "version"], required=False
    )

    assert check.status == "warning"
    assert check.detail == "timed out after 15 seconds"
