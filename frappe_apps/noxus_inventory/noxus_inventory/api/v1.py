import frappe


@frappe.whitelist()
def post_movement(name: str):
    from noxus_core.module_runtime import transition

    return transition(
        "Noxus Stock Movement",
        name,
        "Posted",
        {"Draft": {"Posted", "Cancelled"}, "Posted": {"Cancelled"}, "Cancelled": set()},
    )


@frappe.whitelist()
def stock_balance(item: str, warehouse: str):
    frappe.has_permission("Noxus Stock Movement", "read", throw=True)
    value = frappe.db.sql(
        "select coalesce(sum(case when movement_type='Receipt' then quantity "
        "when movement_type='Issue' then -quantity else quantity end), 0) "
        "from `tabNoxus Stock Movement` where item=%s and warehouse=%s and status='Posted'",
        (item, warehouse),
    )[0][0]
    return {"item": item, "warehouse": warehouse, "quantity": value}
