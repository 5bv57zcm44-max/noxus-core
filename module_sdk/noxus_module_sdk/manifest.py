from __future__ import annotations

import re
from enum import StrEnum

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version
from pydantic import Field, field_validator, model_validator

from noxus_module_sdk.common import MODULE_PATTERN, StrictModel

DEPENDENCY_PATTERN = re.compile(r"^(noxus_[a-z][a-z0-9_]*|erpnext)(.*)$")


class ModuleCategory(StrEnum):
    CORE = "core"
    BUSINESS = "business"
    OPERATIONS = "operations"
    ENTERPRISE = "enterprise"
    INTELLIGENCE = "intelligence"
    INTEGRATION = "integration"


class DependencySpec(StrictModel):
    name: str
    constraint: str = ""

    @classmethod
    def parse(cls, raw: str) -> DependencySpec:
        match = DEPENDENCY_PATTERN.fullmatch(raw.replace(" ", ""))
        if not match:
            raise ValueError(f"Invalid dependency specification: {raw!r}")
        name, constraint = match.groups()
        if constraint:
            try:
                SpecifierSet(constraint)
            except InvalidSpecifier as exc:
                raise ValueError(f"Invalid constraint in dependency {raw!r}") from exc
        return cls(name=name, constraint=constraint)

    def accepts(self, version: str) -> bool:
        try:
            parsed = Version(version)
        except InvalidVersion:
            return False
        return not self.constraint or parsed in SpecifierSet(self.constraint)

    def __str__(self) -> str:
        return f"{self.name}{self.constraint}"


class DependencyGroup(StrictModel):
    required: list[DependencySpec] = Field(default_factory=list)
    recommended: list[DependencySpec] = Field(default_factory=list)
    conflicts: list[DependencySpec] = Field(default_factory=list)

    @field_validator("required", "recommended", "conflicts", mode="before")
    @classmethod
    def parse_specs(cls, value: object) -> object:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("Dependency groups must be lists")
        return [DependencySpec.parse(item) if isinstance(item, str) else item for item in value]


class PlatformRequirements(StrictModel):
    python: str = ">=3.14,<3.15"
    frappe: str = ">=16.28,<17"
    erpnext: str | None = None

    @field_validator("python", "frappe", "erpnext")
    @classmethod
    def validate_specifier(cls, value: str | None) -> str | None:
        if value:
            try:
                SpecifierSet(value)
            except InvalidSpecifier as exc:
                raise ValueError(f"Invalid platform constraint: {value}") from exc
        return value


class ApiDefinition(StrictModel):
    namespace: str

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, value: str) -> str:
        if not value.startswith("/api/v2/method/noxus_") or ".." in value:
            raise ValueError("API namespace must be a versioned NOXUS Frappe method path")
        return value.rstrip("/")


class ModuleManifest(StrictModel):
    schema_version: int = 1
    name: str
    display_name: str
    version: str
    description: str
    publisher: str = "NOXUS AI"
    license: str = "GPL-3.0-or-later"
    category: ModuleCategory
    dependencies: DependencyGroup = Field(default_factory=DependencyGroup)
    platform: PlatformRequirements = Field(default_factory=PlatformRequirements)
    features: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)
    api: ApiDefinition

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not MODULE_PATTERN.fullmatch(value):
            raise ValueError("Module name must use the noxus_<slug> convention")
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        try:
            Version(value)
        except InvalidVersion as exc:
            raise ValueError("Module version must be a valid semantic version") from exc
        return value

    @field_validator("features", "roles", "permissions", "workflows")
    @classmethod
    def unique_values(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Manifest lists cannot contain duplicates")
        return value

    @model_validator(mode="after")
    def validate_contract(self) -> ModuleManifest:
        if self.schema_version != 1:
            raise ValueError("Only manifest schema_version 1 is supported")
        if self.license != "GPL-3.0-or-later":
            raise ValueError("NOXUS v1 modules must use GPL-3.0-or-later")
        referenced = {
            item.name
            for group in (
                self.dependencies.required,
                self.dependencies.recommended,
                self.dependencies.conflicts,
            )
            for item in group
        }
        if self.name in referenced:
            raise ValueError("A module cannot depend on or conflict with itself")
        return self
