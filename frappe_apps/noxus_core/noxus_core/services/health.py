from __future__ import annotations

from typing import Any


def snapshot() -> dict[str, Any]:
    import frappe

    database = "healthy"
    queue = "healthy"
    try:
        frappe.db.sql("select 1")
    except Exception:
        database = "failed"
    try:
        frappe.cache.ping()
    except Exception:
        queue = "failed"
    status = "healthy" if database == queue == "healthy" else "degraded"
    return {"status": status, "site": frappe.local.site, "database": database, "redis": queue}


def run_scheduled_checks() -> None:
    import frappe
    from frappe.utils import now_datetime

    state = snapshot()
    normalized = "runtime"
    values = {
        "check_name": "Runtime",
        "status": state["status"].title(),
        "checked_at": now_datetime(),
        "details": state,
        "lifecycle_state": "Active",
    }
    if frappe.db.exists("System Health Check", normalized):
        frappe.db.set_value("System Health Check", normalized, values)
    else:
        frappe.get_doc(
            {"doctype": "System Health Check", "normalized_id": normalized, **values}
        ).insert(ignore_permissions=True)
