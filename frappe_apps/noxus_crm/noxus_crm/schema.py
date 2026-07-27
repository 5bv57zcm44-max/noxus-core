from noxus_core.module_runtime import operational_schema

ROLES = ["CRM Manager", "Sales User"]
SCHEMAS = [
    operational_schema(
        "Noxus CRM",
        "Noxus Lead",
        [
            {"fieldname": "full_name", "label": "Full Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "email", "label": "Email", "fieldtype": "Data", "options": "Email"},
            {"fieldname": "company", "label": "Company", "fieldtype": "Data"},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "New\nQualified\nDisqualified",
                "default": "New",
                "reqd": 1,
            },
            {"fieldname": "owner_user", "label": "Owner", "fieldtype": "Link", "options": "User"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus CRM",
        "Noxus Opportunity",
        [
            {"fieldname": "title", "label": "Title", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "lead", "label": "Lead", "fieldtype": "Link", "options": "Noxus Lead"},
            {"fieldname": "amount", "label": "Amount", "fieldtype": "Currency"},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Open\nProposal\nWon\nLost",
                "default": "Open",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
]
