from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    USAGE = 2
    PREREQUISITE = 3
    CONFLICT = 4
    CANCELLED = 5
    PARTIAL_FAILURE = 6
    PERMISSION = 7
    UNSAFE = 8
    HEALTH = 9
    NETWORK = 10


class NoxusError(RuntimeError):
    def __init__(self, message: str, *, exit_code: ExitCode = ExitCode.PARTIAL_FAILURE) -> None:
        super().__init__(message)
        self.exit_code = exit_code
