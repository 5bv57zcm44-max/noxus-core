from __future__ import annotations

import hashlib
from typing import Any

from noxus_core.contracts import FeatureUpdateRequest


def resolve_features(module: str | None = None) -> dict[str, bool]:
    import frappe

    definition_filters = {"module": module} if module else {}
    definitions = frappe.get_all(
        "Feature Definition",
        filters=definition_filters,
        fields=["name", "feature_key"],
        order_by="feature_key asc",
    )
    roles = set(frappe.get_roles())
    flags = frappe.get_all("Feature Flag", fields=["feature", "enabled", "scope", "scope_value"])
    effective: dict[str, bool] = {}
    for definition in definitions:
        applicable = [
            flag
            for flag in flags
            if flag.feature == definition.name
            and (
                flag.scope == "Site"
                or (flag.scope == "User" and flag.scope_value == frappe.session.user)
                or (flag.scope == "Role" and flag.scope_value in roles)
            )
        ]
        effective[definition.feature_key] = any(bool(flag.enabled) for flag in applicable)
    return effective


def update_feature(request: FeatureUpdateRequest) -> dict[str, Any]:
    import frappe

    if not frappe.db.exists("Feature Definition", request.feature):
        frappe.throw("Unknown feature definition", frappe.DoesNotExistError)
    scope_value = request.scope_value if request.scope != "Site" else ""
    digest = hashlib.sha256(
        f"{request.feature}:{request.scope}:{scope_value}".encode()
    ).hexdigest()[:16]
    normalized_id = f"{request.feature}.{request.scope.lower()}.{digest}"
    values = {
        "feature": request.feature,
        "enabled": request.enabled,
        "scope": request.scope,
        "scope_value": scope_value,
        "lifecycle_state": "Active",
    }
    if frappe.db.exists("Feature Flag", normalized_id):
        frappe.db.set_value("Feature Flag", normalized_id, values, update_modified=True)
    else:
        frappe.get_doc(
            {"doctype": "Feature Flag", "normalized_id": normalized_id, **values}
        ).insert()
    from noxus_core.services.audit import record_event

    record_event("feature.updated", "Feature Flag", normalized_id, values)
    return {"feature_flag": normalized_id, "enabled": request.enabled, "scope": request.scope}
