from __future__ import annotations

from typing import Any


def ensure_roles() -> None:
    import frappe

    for role_name in ("Noxus Administrator", "Noxus Auditor"):
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
                ignore_permissions=True
            )


def ensure_schemas(schemas: list[dict[str, Any]] | None = None) -> None:
    import frappe

    from noxus_core.schema import CORE_SCHEMAS

    for definition in schemas or CORE_SCHEMAS:
        if not frappe.db.exists("DocType", definition["name"]):
            frappe.get_doc(definition).insert(ignore_permissions=True)
            continue
        existing = frappe.get_doc("DocType", definition["name"])
        if not existing.custom:
            frappe.throw(f"NOXUS schema name collides with standard DocType {existing.name}")
        existing_fields = {item.fieldname for item in existing.fields}
        changed = False
        for field_definition in definition["fields"]:
            if field_definition["fieldname"] not in existing_fields:
                existing.append("fields", field_definition)
                changed = True
        existing_roles = {item.role for item in existing.permissions}
        for permission in definition["permissions"]:
            if permission["role"] not in existing_roles:
                existing.append("permissions", permission)
                changed = True
        if changed:
            existing.save(ignore_permissions=True)


def after_install() -> None:
    ensure_roles()
    ensure_schemas()
    from noxus_core.services.audit import record_event
    from noxus_core.services.registry import synchronize_registry

    synchronize_registry()
    record_event("core.installed", "App", "noxus_core", {"version": "1.0.0rc1"})


def before_uninstall() -> None:
    import frappe

    if frappe.db.count("Installed Module", {"lifecycle_state": "Active"}) > 1:
        frappe.throw("NOXUS Core cannot be removed while dependent NOXUS modules are active")
