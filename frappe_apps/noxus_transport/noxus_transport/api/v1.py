import uuid

import frappe
from frappe.utils import now_datetime


@frappe.whitelist()
def transition_trip(name: str, target: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Transport Trip",
        name,
        target,
        {
            "Draft": {"Dispatched", "Cancelled"},
            "Dispatched": {"In Progress", "Cancelled"},
            "In Progress": {"Complete"},
            "Complete": set(),
            "Cancelled": set(),
        },
    )


@frappe.whitelist()
def record_location(
    trip: str, latitude: float, longitude: float, accuracy_meters: float | None = None
):
    frappe.has_permission("Transport Location Event", "create", throw=True)
    if not -90 <= float(latitude) <= 90 or not -180 <= float(longitude) <= 180:
        frappe.throw("Invalid coordinates")
    doc = frappe.get_doc(
        {
            "doctype": "Transport Location Event",
            "normalized_id": f"loc-{uuid.uuid4()}",
            "trip": trip,
            "recorded_at": now_datetime(),
            "latitude": latitude,
            "longitude": longitude,
            "accuracy_meters": accuracy_meters,
        }
    ).insert()
    return {"name": doc.name, "recorded_at": doc.recorded_at}


@frappe.whitelist()
def trip_summary():
    from noxus_core.module_runtime import summary

    return summary("Transport Trip")
