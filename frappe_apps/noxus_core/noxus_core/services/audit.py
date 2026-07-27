from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any


def record_event(
    action: str, subject_type: str, subject_id: str, payload: dict[str, Any] | None = None
) -> str:
    import frappe
    from frappe.utils import now_datetime

    event_id = str(uuid.uuid4())
    body = payload or {}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    doc = frappe.get_doc(
        {
            "doctype": "Audit Event",
            "normalized_id": event_id,
            "occurred_at": now_datetime(),
            "actor": frappe.session.user if frappe.session.user != "Guest" else None,
            "action": action,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "payload": json.dumps(body, sort_keys=True, default=str),
            "checksum": digest,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def reject_audit_mutation(doc, method: str | None = None) -> None:
    if not doc.is_new():
        import frappe

        frappe.throw("Audit events are immutable", frappe.PermissionError)
