import frappe


@frappe.whitelist()
def pipeline():
    from noxus_core.module_runtime import summary

    return summary("Noxus Opportunity")


@frappe.whitelist()
def transition(name: str, target: str):
    from noxus_core.module_runtime import transition as apply_transition

    return apply_transition(
        "Noxus Opportunity",
        name,
        target,
        {"Open": {"Proposal", "Lost"}, "Proposal": {"Won", "Lost"}, "Won": set(), "Lost": set()},
    )
