from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator

from noxus_module_sdk.common import SLUG_PATTERN, StrictModel


class ProjectType(StrEnum):
    WEBSITE = "website"
    SAAS = "saas"
    FRAPPE_EXISTING = "frappe-existing"


class ProjectConfig(StrictModel):
    schema_version: int = 1
    name: str
    project_type: ProjectType
    environment: Literal["development", "production"] = "development"
    language: Literal["english", "arabic", "both"] = "both"
    database: Literal["postgres", "sqlite", "mariadb"]
    authentication: Literal["jwt", "session", "both"] = "both"
    docker: bool = True
    site_name: str | None = None
    modules: list[str] = Field(default_factory=list)
    with_erpnext: bool = False
    template_version: str = "1.0.0rc1"
    root: Path = Path(".")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("Project name must be a lowercase slug")
        return value

    @field_validator("modules")
    @classmethod
    def unique_modules(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Project modules must be unique")
        return value
