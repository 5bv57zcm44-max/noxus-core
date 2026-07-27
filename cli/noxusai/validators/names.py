from __future__ import annotations

from pathlib import Path

from noxus_module_sdk.common import SLUG_PATTERN


def project_slug(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "-")
    if not SLUG_PATTERN.fullmatch(normalized):
        raise ValueError("Use 3-64 lowercase letters, numbers, and hyphens")
    return normalized


def contained_destination(parent: Path, name: str) -> Path:
    resolved_parent = parent.expanduser().resolve()
    target = (resolved_parent / name).resolve()
    if target.parent != resolved_parent:
        raise ValueError("Project destination escapes the selected directory")
    return target
