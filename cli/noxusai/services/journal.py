from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(slots=True)
class JournalEntry:
    operation: str
    target: str
    status: str
    timestamp: str
    detail: str | None = None


class OperationJournal:
    def __init__(self, project_root: Path) -> None:
        self.path = project_root / ".noxus" / "operations.jsonl"

    def record(self, operation: str, target: str, status: str, detail: str | None = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = JournalEntry(
            operation=operation,
            target=target,
            status=status,
            timestamp=datetime.now(UTC).isoformat(),
            detail=detail,
        )
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
