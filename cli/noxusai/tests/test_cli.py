from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock

from typer.testing import CliRunner

from noxusai.main import app
from noxusai.services.doctor import _command_check

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "1.0.0rc1"


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


def test_optional_doctor_command_timeout_becomes_a_warning(monkeypatch) -> None:
    monkeypatch.setattr("noxusai.services.doctor.shutil.which", lambda _command: "docker")
    process_runner = MagicMock()
    process_runner.run.side_effect = subprocess.TimeoutExpired(("docker", "compose"), 15)

    check = _command_check(
        process_runner, "Docker Compose", ["docker", "compose", "version"], required=False
    )

    assert check.status == "warning"
    assert check.detail == "timed out after 15 seconds"
