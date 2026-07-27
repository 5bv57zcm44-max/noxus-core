from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

import yaml
from noxus_module_sdk.project import ProjectConfig
from noxusai.errors import ExitCode, NoxusError
from platformdirs import user_config_path

REDACT_KEYS = {"password", "secret", "token", "api_key", "admin_password"}


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".noxus" / "project.yml").is_file():
            return candidate
    return None


def load_project(start: Path) -> ProjectConfig:
    root = find_project_root(start)
    if root is None:
        raise NoxusError(
            "No NOXUS project found. Run `noxusai new` or `noxusai init` first.",
            exit_code=ExitCode.USAGE,
        )
    path = root / ".noxus" / "project.yml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise NoxusError(f"Invalid project configuration: {path}")
    raw["root"] = root
    return ProjectConfig.model_validate(raw)


def write_project(config: ProjectConfig, root: Path) -> Path:
    target = root / ".noxus" / "project.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = config.model_dump(mode="json", exclude={"root"}, exclude_none=True)
    target.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    return target


def user_config() -> dict[str, Any]:
    path = user_config_path("noxusai") / "config.toml"
    if not path.is_file():
        return {}
    with path.open("rb") as stream:
        raw = tomllib.load(stream)
    return raw if isinstance(raw, dict) else {}


def merged_config(project: ProjectConfig | None = None) -> dict[str, Any]:
    merged: dict[str, Any] = user_config()
    if project:
        merged.update(project.model_dump(mode="json", exclude_none=True))
    for key, value in os.environ.items():
        if key.startswith("NOXUS_"):
            merged[key[6:].lower()] = value
    return merged


def redacted_config(value: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, item in value.items():
        if any(secret in key.lower() for secret in REDACT_KEYS):
            output[key] = "<redacted>"
        elif isinstance(item, dict):
            output[key] = redacted_config(item)
        else:
            output[key] = item
    return output
