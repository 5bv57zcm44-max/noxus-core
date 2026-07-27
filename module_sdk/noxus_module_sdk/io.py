from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def load_yaml(path: Path, model: type[ModelT]) -> ModelT:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return model.model_validate(raw)


def dump_yaml(value: BaseModel, path: Path) -> None:
    path.write_text(
        yaml.safe_dump(value.model_dump(mode="json", exclude_none=True), sort_keys=False),
        encoding="utf-8",
    )


def json_schema(model: type[BaseModel]) -> dict[str, object]:
    return model.model_json_schema()
