from noxus_core.module_runtime import operational_schema

ROLES = ["Inventory Manager", "Stock User"]
SCHEMAS = [
    operational_schema(
        "Noxus Inventory",
        "Noxus Item",
        [
            {"fieldname": "item_name", "label": "Item Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "unit", "label": "Unit", "fieldtype": "Data", "default": "Unit"},
            {
                "fieldname": "reorder_level",
                "label": "Reorder Level",
                "fieldtype": "Float",
                "default": "0",
            },
            {
                "fieldname": "erpnext_item",
                "label": "ERPNext Item",
                "fieldtype": "Dynamic Link",
                "options": "erpnext_reference_type",
            },
            {
                "fieldname": "erpnext_reference_type",
                "label": "ERPNext Reference Type",
                "fieldtype": "Link",
                "options": "DocType",
                "hidden": 1,
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Inventory",
        "Noxus Warehouse",
        [
            {
                "fieldname": "warehouse_name",
                "label": "Warehouse Name",
                "fieldtype": "Data",
                "reqd": 1,
            },
            {"fieldname": "location", "label": "Location", "fieldtype": "Data"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Inventory",
        "Noxus Stock Movement",
        [
            {
                "fieldname": "item",
                "label": "Item",
                "fieldtype": "Link",
                "options": "Noxus Item",
                "reqd": 1,
            },
            {
                "fieldname": "warehouse",
                "label": "Warehouse",
                "fieldtype": "Link",
                "options": "Noxus Warehouse",
                "reqd": 1,
            },
            {"fieldname": "quantity", "label": "Quantity", "fieldtype": "Float", "reqd": 1},
            {
                "fieldname": "movement_type",
                "label": "Movement Type",
                "fieldtype": "Select",
                "options": "Receipt\nIssue\nAdjustment",
                "reqd": 1,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Draft\nPosted\nCancelled",
                "default": "Draft",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
]
