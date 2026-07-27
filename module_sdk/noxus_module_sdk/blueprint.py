from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from noxus_module_sdk.common import MODULE_PATTERN, SLUG_PATTERN, StrictModel, checksum


class BlueprintModule(StrictModel):
    name: str
    version: str
    features: list[str] = Field(default_factory=list)
    install_order: int = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not MODULE_PATTERN.fullmatch(value) and value != "erpnext":
            raise ValueError("Invalid blueprint module name")
        return value


class BlueprintBranding(StrictModel):
    product_name: str = "NOXUS CORE"
    accent_color: str = "#4F46E5"
    logo_path: str | None = None
    default_direction: Literal["ltr", "rtl"] = "ltr"

    @field_validator("accent_color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("Accent color must be a six-digit hexadecimal color")
        int(value[1:], 16)
        return value.upper()


class DeploymentProfile(StrictModel):
    environment: Literal["development", "production"] = "development"
    with_erpnext: bool = False
    http_port: int = Field(default=8080, ge=1, le=65535)


class SolutionBlueprint(StrictModel):
    schema_version: int = 1
    name: str
    industry: str
    language: Literal["english", "arabic", "both"] = "both"
    modules: list[BlueprintModule] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    branding: BlueprintBranding = Field(default_factory=BlueprintBranding)
    deployment: DeploymentProfile = Field(default_factory=DeploymentProfile)
    generated_by: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    checksum: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not SLUG_PATTERN.fullmatch(value):
            raise ValueError("Blueprint name must be a lowercase slug")
        return value

    @model_validator(mode="after")
    def validate_blueprint(self) -> SolutionBlueprint:
        if self.schema_version != 1:
            raise ValueError("Only blueprint schema_version 1 is supported")
        names = [module.name for module in self.modules]
        if len(names) != len(set(names)):
            raise ValueError("Blueprint modules must be unique")
        orders = [module.install_order for module in self.modules]
        if sorted(orders) != list(range(len(orders))):
            raise ValueError("Blueprint install_order values must be contiguous from zero")
        if self.deployment.with_erpnext and "erpnext" not in names:
            raise ValueError("ERPNext deployment requires an erpnext module entry")
        return self

    def seal(self) -> SolutionBlueprint:
        raw = self.model_copy(update={"checksum": None})
        self.checksum = checksum(raw)
        return self

    def verify_checksum(self) -> bool:
        if not self.checksum:
            return False
        raw = self.model_copy(update={"checksum": None})
        return self.checksum == checksum(raw)
