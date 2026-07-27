import uuid

import frappe


@frappe.whitelist()
def mark_attendance(session: str, student: str, status: str):
    if status not in {"Present", "Absent", "Late", "Excused"}:
        frappe.throw("Invalid attendance state")
    frappe.has_permission("Education Attendance", "create", throw=True)
    existing = frappe.db.get_value(
        "Education Attendance", {"session": session, "student": student}, "name"
    )
    if existing:
        doc = frappe.get_doc("Education Attendance", existing)
        doc.check_permission("write")
        doc.status = status
        doc.recorded_by = frappe.session.user
        doc.save()
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Education Attendance",
                "normalized_id": f"attendance-{uuid.uuid4()}",
                "session": session,
                "student": student,
                "status": status,
                "recorded_by": frappe.session.user,
            }
        ).insert()
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def attendance_report(session: str):
    frappe.has_permission("Education Attendance", "read", throw=True)
    return frappe.get_list(
        "Education Attendance",
        filters={"session": session},
        fields=["student", "status", "recorded_by", "modified"],
    )


@frappe.whitelist()
def transition_enrollment(name: str, target: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Education Enrollment",
        name,
        target,
        {
            "Pending": {"Active", "Rejected"},
            "Active": {"Completed"},
            "Rejected": set(),
            "Completed": set(),
        },
    )
