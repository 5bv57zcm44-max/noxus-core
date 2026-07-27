from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from pydantic import BaseModel, ConfigDict

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,62}[a-z0-9]$")
MODULE_PATTERN = re.compile(r"^noxus_[a-z](?:[a-z0-9_]{0,56}[a-z0-9])?$")


class StrictModel(BaseModel):
    """Base contract that rejects misspelled or forward-version fields."""

    model_config = ConfigDict(extra="forbid", frozen=False, str_strip_whitespace=True)


def canonical_json(value: BaseModel | dict[str, Any]) -> str:
    raw = (
        value.model_dump(mode="json", exclude_none=True) if isinstance(value, BaseModel) else value
    )
    return json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def checksum(value: BaseModel | dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()
