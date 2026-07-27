from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from noxusai.context import RuntimeContext
from noxusai.errors import NoxusError

SECRET_PATTERN = re.compile(r"(?i)(password|secret|token|api[_-]?key)=([^\s]+)")


def redact(value: str) -> str:
    return SECRET_PATTERN.sub(r"\1=<redacted>", value)


@dataclass(slots=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class ProcessRunner:
    def __init__(self, context: RuntimeContext) -> None:
        self.context = context

    def run(
        self,
        args: Sequence[str],
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
        check: bool = True,
        timeout: int = 300,
        stdin_text: str | None = None,
    ) -> CommandResult:
        if not args or not all(isinstance(item, str) and item for item in args):
            raise ValueError("Commands must be non-empty string argument arrays")
        safe_args = tuple(args)
        if self.context.verbose or self.context.dry_run:
            shown = " ".join(redact(item) for item in safe_args)
            self.context.console.print(f"[dim]$ {shown}[/dim]")
        if self.context.dry_run:
            return CommandResult(safe_args, 0, "", "")
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        completed = subprocess.run(  # noqa: S603 - arguments are validated arrays
            safe_args,
            cwd=cwd,
            env=process_env,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            input=stdin_text,
        )
        result = CommandResult(
            args=safe_args,
            returncode=completed.returncode,
            stdout=redact(completed.stdout.strip()),
            stderr=redact(completed.stderr.strip()),
        )
        if check and result.returncode:
            detail = result.stderr or result.stdout or "command failed without output"
            raise NoxusError(f"Command failed ({result.returncode}): {detail}")
        return result
