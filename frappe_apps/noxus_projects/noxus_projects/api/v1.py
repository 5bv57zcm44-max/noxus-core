import frappe


@frappe.whitelist()
def task_board(project: str):
    return frappe.get_list(
        "Noxus Task",
        filters={"project": project},
        fields=["name", "title", "status", "assigned_to", "due_date"],
        order_by="status asc, due_date asc",
    )


@frappe.whitelist()
def transition_task(name: str, target: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Noxus Task",
        name,
        target,
        {
            "Open": {"Doing", "Blocked"},
            "Doing": {"Done", "Blocked"},
            "Blocked": {"Doing"},
            "Done": set(),
        },
    )
