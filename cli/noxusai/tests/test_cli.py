from __future__ import annotations

import json

from typer.testing import CliRunner

from noxusai.main import app

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
