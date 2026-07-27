from __future__ import annotations

from pydantic import Field, field_validator

from noxus_module_sdk.common import StrictModel


class RuntimeVersions(StrictModel):
    python: str = "3.14.6"
    frappe: str = "16.28.0"
    erpnext: str = "16.29.0"
    node: str = "24.18.0"
    mariadb: str = "11.8.6"
    redis: str = "7.2.14"


class PayloadFile(StrictModel):
    path: str
    sha256: str
    size: int = Field(ge=0)

    @field_validator("path")
    @classmethod
    def safe_path(cls, value: str) -> str:
        if value.startswith(("/", "\\")) or ".." in value.replace("\\", "/").split("/"):
            raise ValueError("Release payload paths must be relative and contained")
        return value.replace("\\", "/")

    @field_validator("sha256")
    @classmethod
    def valid_hash(cls, value: str) -> str:
        if len(value) != 64:
            raise ValueError("SHA-256 values must contain 64 hexadecimal characters")
        int(value, 16)
        return value.lower()


class ReleaseManifest(StrictModel):
    schema_version: int = 1
    noxus_version: str
    versions: RuntimeVersions = Field(default_factory=RuntimeVersions)
    files: list[PayloadFile] = Field(default_factory=list)
    image_digests: dict[str, str] = Field(default_factory=dict)
