import frappe


@frappe.whitelist()
def provider_health(name: str):
    from noxus_ai.service import health

    return health(name)


@frappe.whitelist()
def providers():
    frappe.has_permission("AI Provider Configuration", "read", throw=True)
    return frappe.get_list(
        "AI Provider Configuration",
        fields=["name", "provider_name", "base_url", "status", "timeout_seconds"],
    )
