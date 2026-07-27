from __future__ import annotations

import subprocess

import pytest

from noxusai.context import RuntimeContext
from noxusai.services.process import ProcessRunner, redact


def test_redact_hides_secret_values() -> None:
    assert redact("token=abc password=hunter2") == "token=<redacted> password=<redacted>"


def test_runner_uses_argument_array_without_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(args: tuple[str, ...], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured.update(kwargs)
        return subprocess.CompletedProcess(args, 0, "ok", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = ProcessRunner(RuntimeContext()).run(["tool", "value with spaces"])
    assert result.stdout == "ok"
    assert captured["args"] == ("tool", "value with spaces")
    assert captured["shell"] is False
