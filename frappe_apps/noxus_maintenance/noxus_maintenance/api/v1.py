import frappe


@frappe.whitelist()
def transition_work_order(name: str, target: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Maintenance Work Order",
        name,
        target,
        {
            "Draft": {"Scheduled", "Cancelled"},
            "Scheduled": {"In Progress", "Cancelled"},
            "In Progress": {"Blocked", "Complete"},
            "Blocked": {"In Progress", "Cancelled"},
            "Complete": set(),
            "Cancelled": set(),
        },
    )


@frappe.whitelist()
def workload():
    from noxus_core.module_runtime import summary

    return summary("Maintenance Work Order")


@frappe.whitelist()
def due_schedules(until: str):
    frappe.has_permission("Preventive Maintenance Schedule", "read", throw=True)
    return frappe.get_list(
        "Preventive Maintenance Schedule",
        filters={"next_due": ["<=", until], "status": "Active"},
        fields=["name", "asset", "next_due", "frequency_days"],
    )
