from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ResolveRequest(Contract):
    modules: list[str]
    platform: dict[str, str] = Field(
        default_factory=lambda: {"python": "3.14.6", "frappe": "16.28.0"}
    )


class BlueprintModule(Contract):
    name: str
    version: str
    features: list[str] = Field(default_factory=list)
    install_order: int = Field(ge=0)


class BlueprintRequest(Contract):
    schema_version: Literal[1] = 1
    name: str = Field(min_length=2, max_length=80)
    industry: str
    language: Literal["english", "arabic", "both"] = "both"
    modules: list[BlueprintModule]
    roles: list[str] = Field(default_factory=list)
    workflows: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    branding: dict[str, Any] = Field(default_factory=dict)
    deployment: dict[str, Any] = Field(default_factory=dict)
    generator_version: str
    checksum: str

    @field_validator("name")
    @classmethod
    def slug(cls, value: str) -> str:
        if not value or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in value
        ):
            raise ValueError("Blueprint name must be a lowercase slug")
        return value


class ApplyRequest(Contract):
    blueprint: BlueprintRequest
    idempotency_key: str = Field(min_length=16, max_length=128)

    @field_validator("idempotency_key")
    @classmethod
    def normalized_idempotency_key(cls, value: str) -> str:
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]+", value):
            raise ValueError("Idempotency keys must be normalized lowercase identifiers")
        return value


class ResumeRequest(Contract):
    deployment: str = Field(min_length=1, max_length=140)
    resume_token: str = Field(min_length=32, max_length=256)


class FeatureUpdateRequest(Contract):
    feature: str = Field(min_length=2, max_length=140)
    enabled: bool
    scope: Literal["Site", "User", "Role"] = "Site"
    scope_value: str = Field(default="", max_length=140)

    @field_validator("scope_value")
    @classmethod
    def scope_target(cls, value: str, info) -> str:
        scope = info.data.get("scope", "Site")
        if scope != "Site" and not value.strip():
            raise ValueError("User and Role feature flags require scope_value")
        return value.strip()


class DeploymentStatusRequest(Contract):
    deployment: str = Field(min_length=1, max_length=140)


class ValidationRequest(Contract):
    kind: Literal["blueprint", "resolution"]
    value: dict[str, Any]


class AutomationAction(Contract):
    action_type: Literal[
        "Notification", "Assignment", "Field Change", "Create Document", "Signed Webhook"
    ]
    config: dict[str, Any]


def parse(model: type[Contract], value: str | dict[str, Any]) -> Contract:
    raw = json.loads(value) if isinstance(value, str) else value
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        import frappe

        frappe.throw(str(exc), frappe.ValidationError)
        raise
