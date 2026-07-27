from noxus_core.module_runtime import operational_schema

ROLES = ["AI Integration Manager"]
SCHEMAS = [
    operational_schema(
        "Noxus AI",
        "AI Provider Configuration",
        [
            {
                "fieldname": "provider_name",
                "label": "Provider Name",
                "fieldtype": "Data",
                "reqd": 1,
            },
            {"fieldname": "base_url", "label": "Base URL", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "allowed_hostname",
                "label": "Allowed Hostname",
                "fieldtype": "Data",
                "reqd": 1,
            },
            {"fieldname": "credential", "label": "Credential", "fieldtype": "Password"},
            {
                "fieldname": "timeout_seconds",
                "label": "Timeout Seconds",
                "fieldtype": "Int",
                "default": "15",
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Disabled\nEnabled\nUnhealthy",
                "default": "Disabled",
                "reqd": 1,
            },
        ],
        ROLES,
    ),
]
