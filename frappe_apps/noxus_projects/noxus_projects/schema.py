from noxus_core.module_runtime import operational_schema

ROLES = ["Project Manager", "Project User"]
SCHEMAS = [
    operational_schema(
        "Noxus Projects",
        "Noxus Project",
        [
            {"fieldname": "title", "label": "Title", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Planned\nActive\nOn Hold\nComplete",
                "default": "Planned",
            },
            {"fieldname": "starts_on", "label": "Starts On", "fieldtype": "Date"},
            {"fieldname": "ends_on", "label": "Ends On", "fieldtype": "Date"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Projects",
        "Noxus Task",
        [
            {
                "fieldname": "project",
                "label": "Project",
                "fieldtype": "Link",
                "options": "Noxus Project",
                "reqd": 1,
            },
            {"fieldname": "title", "label": "Title", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "assigned_to",
                "label": "Assigned To",
                "fieldtype": "Link",
                "options": "User",
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Open\nDoing\nBlocked\nDone",
                "default": "Open",
            },
            {"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date"},
        ],
        ROLES,
    ),
]
