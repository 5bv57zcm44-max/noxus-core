from noxus_core.module_runtime import operational_schema

ROLES = ["Maintenance Manager", "Maintenance Supervisor", "Technician", "Viewer"]
SCHEMAS = [
    operational_schema(
        "Noxus Maintenance",
        "Maintenance Asset",
        [
            {"fieldname": "asset_name", "label": "Asset Name", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "serial_number",
                "label": "Serial Number",
                "fieldtype": "Data",
                "unique": 1,
            },
            {"fieldname": "location", "label": "Location", "fieldtype": "Data"},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Active\nOut of Service\nRetired",
                "default": "Active",
            },
            {
                "fieldname": "erpnext_asset",
                "label": "ERPNext Asset",
                "fieldtype": "Data",
                "description": (
                    "Optional adapter reference; validated only when ERPNext is installed"
                ),
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Maintenance Request",
        [
            {
                "fieldname": "asset",
                "label": "Asset",
                "fieldtype": "Link",
                "options": "Maintenance Asset",
                "reqd": 1,
            },
            {"fieldname": "subject", "label": "Subject", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "description", "label": "Description", "fieldtype": "Text Editor"},
            {
                "fieldname": "priority",
                "label": "Priority",
                "fieldtype": "Select",
                "options": "Low\nNormal\nHigh\nCritical",
                "default": "Normal",
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "New\nApproved\nRejected\nConverted",
                "default": "New",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Maintenance Work Order",
        [
            {
                "fieldname": "request",
                "label": "Request",
                "fieldtype": "Link",
                "options": "Maintenance Request",
            },
            {
                "fieldname": "asset",
                "label": "Asset",
                "fieldtype": "Link",
                "options": "Maintenance Asset",
                "reqd": 1,
            },
            {
                "fieldname": "technician",
                "label": "Technician",
                "fieldtype": "Link",
                "options": "Maintenance Technician",
            },
            {"fieldname": "scheduled_for", "label": "Scheduled For", "fieldtype": "Datetime"},
            {
                "fieldname": "completed_at",
                "label": "Completed At",
                "fieldtype": "Datetime",
                "read_only": 1,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Draft\nScheduled\nIn Progress\nBlocked\nComplete\nCancelled",
                "default": "Draft",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Maintenance Technician",
        [
            {
                "fieldname": "user",
                "label": "User",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1,
            },
            {"fieldname": "skills", "label": "Skills", "fieldtype": "Small Text"},
            {"fieldname": "available", "label": "Available", "fieldtype": "Check", "default": "1"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Preventive Maintenance Schedule",
        [
            {
                "fieldname": "asset",
                "label": "Asset",
                "fieldtype": "Link",
                "options": "Maintenance Asset",
                "reqd": 1,
            },
            {
                "fieldname": "frequency_days",
                "label": "Frequency Days",
                "fieldtype": "Int",
                "reqd": 1,
            },
            {"fieldname": "next_due", "label": "Next Due", "fieldtype": "Date", "reqd": 1},
            {"fieldname": "instructions", "label": "Instructions", "fieldtype": "Text Editor"},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Active\nPaused",
                "default": "Active",
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Spare Part Requirement",
        [
            {
                "fieldname": "work_order",
                "label": "Work Order",
                "fieldtype": "Link",
                "options": "Maintenance Work Order",
                "reqd": 1,
            },
            {
                "fieldname": "item",
                "label": "Inventory Item",
                "fieldtype": "Link",
                "options": "Noxus Item",
                "reqd": 1,
            },
            {"fieldname": "quantity", "label": "Quantity", "fieldtype": "Float", "reqd": 1},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Required\nReserved\nIssued",
                "default": "Required",
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Maintenance",
        "Maintenance Attachment",
        [
            {
                "fieldname": "work_order",
                "label": "Work Order",
                "fieldtype": "Link",
                "options": "Maintenance Work Order",
                "reqd": 1,
            },
            {"fieldname": "attachment", "label": "Attachment", "fieldtype": "Attach", "reqd": 1},
            {"fieldname": "caption", "label": "Caption", "fieldtype": "Data"},
        ],
        ROLES,
    ),
]
