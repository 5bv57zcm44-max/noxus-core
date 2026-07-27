from __future__ import annotations


def install_roles(roles: list[str]) -> list[str]:
    import frappe

    installed: list[str] = []
    for role_name in roles:
        if not role_name or len(role_name) > 140:
            frappe.throw("Invalid role name")
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
                ignore_permissions=True
            )
        installed.append(role_name)
    return installed
