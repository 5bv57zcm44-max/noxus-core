from __future__ import annotations

import hashlib
import json
import re
from typing import Any

NORMALIZED_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,139}$")


def operational_schema(
    module: str,
    name: str,
    fields: list[dict[str, Any]],
    roles: list[str],
) -> dict[str, Any]:
    return {
        "doctype": "DocType",
        "name": name,
        "module": module,
        "custom": 1,
        "autoname": "field:normalized_id",
        "track_changes": 1,
        "fields": [
            {
                "fieldname": "normalized_id",
                "label": "Normalized ID",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
            },
            {
                "fieldname": "record_version",
                "label": "Record Version",
                "fieldtype": "Int",
                "default": "1",
                "reqd": 1,
            },
            {"fieldname": "checksum", "label": "Checksum", "fieldtype": "Data", "read_only": 1},
            *fields,
        ],
        "permissions": [
            {
                "role": role,
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
                "export": 1,
            }
            for role in roles
        ],
    }


def ensure_module(schemas: list[dict[str, Any]], roles: list[str]) -> None:
    import frappe

    from noxus_core.install import ensure_schemas

    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)
    ensure_schemas(schemas)
    from noxus_core.services.registry import synchronize_registry

    synchronize_registry()


def validate_record(doc, method: str | None = None) -> None:
    import frappe

    if not NORMALIZED_ID.fullmatch(doc.normalized_id or ""):
        frappe.throw(
            "Normalized ID must contain only lowercase letters, digits, dots, "
            "underscores, and hyphens"
        )
    values = {
        field.fieldname: doc.get(field.fieldname)
        for field in doc.meta.fields
        if field.fieldname not in {"checksum", "modified", "modified_by"}
    }
    doc.checksum = hashlib.sha256(
        json.dumps(values, default=str, sort_keys=True).encode()
    ).hexdigest()
    if not doc.is_new() and doc.has_value_changed("checksum"):
        doc.record_version = (doc.record_version or 0) + 1


def transition(
    doctype: str, name: str, target: str, allowed: dict[str, set[str]]
) -> dict[str, str]:
    import frappe

    doc = frappe.get_doc(doctype, name)
    doc.check_permission("write")
    current = doc.status
    valid_targets = allowed.get(current, set())
    if target not in valid_targets:
        frappe.throw(f"Invalid transition from {current} to {target}")
    doc.status = target
    doc.save()
    from noxus_core.services.audit import record_event

    record_event("workflow.transition", doctype, name, {"from": current, "to": target})
    return {"doctype": doctype, "name": name, "status": target}


def summary(doctype: str, status_field: str = "status") -> list[dict[str, Any]]:
    import frappe

    allowed = {
        item["name"] for item in frappe.get_all("DocType", filters={"custom": 1}, fields=["name"])
    }
    if doctype not in allowed or status_field != "status":
        frappe.throw("Report type is not allow-listed")
    return frappe.db.sql(
        f"select `status` as label, count(*) as value from `tab{doctype}` group by `status`",  # noqa: S608 -- validated against server-owned DocType names
        as_dict=True,
    )
