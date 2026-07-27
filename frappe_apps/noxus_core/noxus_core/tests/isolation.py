"""Bench-only helpers for the opt-in two-site acceptance test."""

from __future__ import annotations

import json


def create_marker() -> str:
    import frappe

    site = str(frappe.local.site)
    values = {
        "display_name": site,
        "description": "Tenant-isolation acceptance marker",
        "publisher": "NOXUS acceptance suite",
        "license": "GPL-3.0-or-later",
        "category": "Test",
        "manifest_json": json.dumps({"test": True}, sort_keys=True),
        "lifecycle_state": "Active",
    }
    if frappe.db.exists("Noxus Module", "shared-isolation-marker"):
        frappe.db.set_value(
            "Noxus Module", "shared-isolation-marker", values, update_modified=False
        )
    else:
        frappe.get_doc(
            {
                "doctype": "Noxus Module",
                "normalized_id": "shared-isolation-marker",
                **values,
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()
    return site


def get_marker() -> str | None:
    import frappe

    return frappe.db.get_value("Noxus Module", "shared-isolation-marker", "display_name")
