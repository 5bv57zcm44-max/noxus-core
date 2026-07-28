from __future__ import annotations

from typing import Any

import frappe

from noxus_core.contracts import (
    ApplyRequest,
    DeploymentStatusRequest,
    FeatureUpdateRequest,
    ResolveRequest,
    ResumeRequest,
    ValidationRequest,
    parse,
)


def _require(role: str = "Noxus Administrator") -> None:
    if role not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        frappe.throw("Not permitted", frappe.PermissionError)


@frappe.whitelist()
def catalog() -> dict[str, Any]:
    _require()
    from noxus_core.services.registry import installed_manifests

    return {
        "modules": installed_manifests(),
        "remote_marketplace": {
            "available": False,
            "reason": "Community v1 lists local modules only",
        },
    }


@frappe.whitelist()
def resolve_modules(request: str | dict[str, Any]) -> dict[str, Any]:
    _require()
    value = parse(ResolveRequest, request)
    from noxus_core.services.dependencies import resolve
    from noxus_core.services.registry import installed_manifests

    assert isinstance(value, ResolveRequest)
    return resolve(installed_manifests(), value.modules, value.platform)


@frappe.whitelist()
def apply_blueprint(request: str | dict[str, Any]) -> dict[str, str]:
    _require("System Manager")
    value = parse(ApplyRequest, request)
    from noxus_core.services.blueprints import queue_application

    assert isinstance(value, ApplyRequest)
    return queue_application(value)


@frappe.whitelist(allow_guest=True)
def health() -> dict[str, Any]:
    if frappe.session.user == "Guest":
        return {"status": "healthy"}
    from noxus_core.services.health import snapshot

    return snapshot()


@frappe.whitelist()
def upgrade_preflight() -> dict[str, object]:
    _require("System Manager")
    from noxus_core.services.upgrades import preflight

    return preflight()


@frappe.whitelist()
def feature_flags(module: str | None = None) -> dict[str, bool]:
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.AuthenticationError)
    from noxus_core.services.features import resolve_features

    return resolve_features(module)


@frappe.whitelist()
def update_feature(request: str | dict[str, Any]) -> dict[str, Any]:
    _require()
    value = parse(FeatureUpdateRequest, request)
    from noxus_core.services.features import update_feature as apply_update

    assert isinstance(value, FeatureUpdateRequest)
    return apply_update(value)


@frappe.whitelist()
def deployment_status(request: str | dict[str, Any]) -> dict[str, Any]:
    _require()
    value = parse(DeploymentStatusRequest, request)
    from noxus_core.services.deployments import status

    assert isinstance(value, DeploymentStatusRequest)
    return status(value.deployment)


@frappe.whitelist()
def resume_deployment(request: str | dict[str, Any]) -> dict[str, str]:
    _require("System Manager")
    value = parse(ResumeRequest, request)
    from noxus_core.services.deployments import resume

    assert isinstance(value, ResumeRequest)
    return resume(value)


@frappe.whitelist()
def validate_configuration(request: str | dict[str, Any]) -> dict[str, Any]:
    _require()
    value = parse(ValidationRequest, request)
    from noxus_core.services.validation import validate_configuration as validate

    assert isinstance(value, ValidationRequest)
    return validate(value.kind, value.value)
