from noxus_core.module_runtime import operational_schema

ROLES = ["Support Manager", "Support Agent"]
SCHEMAS = [
    operational_schema(
        "Noxus Support",
        "Noxus Support Ticket",
        [
            {"fieldname": "subject", "label": "Subject", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "description",
                "label": "Description",
                "fieldtype": "Text Editor",
                "reqd": 1,
            },
            {
                "fieldname": "requester_email",
                "label": "Requester Email",
                "fieldtype": "Data",
                "options": "Email",
            },
            {
                "fieldname": "assigned_to",
                "label": "Assigned To",
                "fieldtype": "Link",
                "options": "User",
            },
            {
                "fieldname": "priority",
                "label": "Priority",
                "fieldtype": "Select",
                "options": "Low\nNormal\nHigh\nUrgent",
                "default": "Normal",
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Open\nIn Progress\nWaiting\nResolved\nClosed",
                "default": "Open",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
]
