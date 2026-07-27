from __future__ import annotations


def _roles(user: str | None) -> set[str]:
    import frappe

    return set(frappe.get_roles(user or frappe.session.user))


def has_permission(doc, ptype: str, user: str | None = None, **_kwargs):
    roles = _roles(user)
    if "System Manager" in roles or "Noxus Administrator" in roles:
        return True
    if doc.doctype == "Audit Event":
        return ptype == "read" and "Noxus Auditor" in roles
    if ptype == "read" and getattr(doc, "owner", None) == (user or ""):
        return True
    return None


def audit_query(user: str | None = None) -> str:
    return "" if {"System Manager", "Noxus Auditor"} & _roles(user) else "1=0"
