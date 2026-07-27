from __future__ import annotations

import pytest
from noxus_module_sdk.manifest import ModuleManifest
from pydantic import ValidationError


def manifest(name: str, required: list[str] | None = None) -> ModuleManifest:
    return ModuleManifest.model_validate(
        {
            "schema_version": 1,
            "name": name,
            "display_name": name.replace("_", " ").title(),
            "version": "1.0.0",
            "description": "A functional test module",
            "category": "operations",
            "dependencies": {"required": required or []},
            "features": ["records"],
            "roles": ["Manager"],
            "permissions": [f"{name}.read"],
            "api": {"namespace": f"/api/v2/method/{name}.api.v1"},
        }
    )


def test_manifest_parses_dependency_shorthand() -> None:
    value = manifest("noxus_maintenance", ["noxus_core>=1.0.0"])
    assert value.dependencies.required[0].name == "noxus_core"
    assert value.dependencies.required[0].accepts("1.2.0")


def test_manifest_rejects_extra_fields() -> None:
    raw = manifest("noxus_core").model_dump(mode="json")
    raw["typo"] = True
    with pytest.raises(ValidationError):
        ModuleManifest.model_validate(raw)
