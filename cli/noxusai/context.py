from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rich.console import Console


@dataclass(slots=True)
class RuntimeContext:
    dry_run: bool = False
    verbose: bool = False
    json_output: bool = False
    no_color: bool = False
    cwd: Path = field(default_factory=Path.cwd)
    console: Console = field(init=False)

    def __post_init__(self) -> None:
        self.console = Console(no_color=self.no_color, stderr=False)

    def emit(
        self,
        command: str,
        data: Any = None,
        *,
        warnings: list[str] | None = None,
    ) -> None:
        import json

        warning_list = warnings or []
        if self.json_output:
            self.console.print_json(
                json.dumps(
                    {
                        "ok": True,
                        "command": command,
                        "data": data,
                        "warnings": warning_list,
                        "error": None,
                    },
                    default=str,
                )
            )
            return
        if isinstance(data, str):
            self.console.print(data)
        elif data is not None:
            self.console.print(data)
        for warning in warning_list:
            self.console.print(f"[yellow]![/yellow] {warning}")


def runtime(ctx: Any) -> RuntimeContext:
    value = ctx.ensure_object(RuntimeContext)
    if not isinstance(value, RuntimeContext):
        raise TypeError("Invalid NOXUS CLI context")
    return value
