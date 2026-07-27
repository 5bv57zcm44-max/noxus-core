from __future__ import annotations

from typing import Any

ALLOWED_FIELD_CHANGES = {"status", "priority", "assigned_to", "lifecycle_state"}
ALLOWED_DOCUMENT_TYPES = {"ToDo", "Communication", "Notification Log"}


def execute(action_type: str, config: dict[str, Any], document) -> None:
    import frappe

    if action_type == "Notification":
        frappe.publish_realtime("noxus_notification", config, user=config.get("user"))
    elif action_type == "Assignment":
        frappe.get_doc(
            {
                "doctype": "ToDo",
                "allocated_to": config["user"],
                "reference_type": document.doctype,
                "reference_name": document.name,
                "description": config.get("description", "NOXUS assignment"),
            }
        ).insert(ignore_permissions=True)
    elif action_type == "Field Change":
        fieldname = config.get("field")
        if fieldname not in ALLOWED_FIELD_CHANGES:
            frappe.throw("Automation attempted a non-allow-listed field change")
        document.db_set(fieldname, config.get("value"), notify=True)
    elif action_type == "Create Document":
        doctype = config.get("doctype")
        if doctype not in ALLOWED_DOCUMENT_TYPES:
            frappe.throw("Automation attempted an unknown document type")
        frappe.get_doc({"doctype": doctype, **config.get("values", {})}).insert(
            ignore_permissions=True
        )
    elif action_type == "Signed Webhook":
        from noxus_core.services.webhooks import deliver

        deliver(config["endpoint"], {"doctype": document.doctype, "name": document.name})
    else:
        frappe.throw("Unsupported automation action")
