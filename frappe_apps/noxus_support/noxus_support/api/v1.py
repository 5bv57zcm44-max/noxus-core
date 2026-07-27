import frappe


@frappe.whitelist()
def transition_ticket(name: str, target: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Noxus Support Ticket",
        name,
        target,
        {
            "Open": {"In Progress", "Closed"},
            "In Progress": {"Waiting", "Resolved"},
            "Waiting": {"In Progress"},
            "Resolved": {"Closed", "In Progress"},
            "Closed": set(),
        },
    )


@frappe.whitelist()
def dashboard():
    from noxus_core.module_runtime import summary

    return summary("Noxus Support Ticket")
