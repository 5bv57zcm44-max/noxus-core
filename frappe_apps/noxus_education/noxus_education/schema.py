from noxus_core.module_runtime import operational_schema

ROLES = ["Education Manager", "Supervisor", "Teacher", "Education Viewer"]
SCHEMAS = [
    operational_schema(
        "Noxus Education",
        "Education Teacher",
        [
            {
                "fieldname": "user",
                "label": "User",
                "fieldtype": "Link",
                "options": "User",
                "reqd": 1,
            },
            {"fieldname": "display_name", "label": "Display Name", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "specialisms", "label": "Specialisms", "fieldtype": "Small Text"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Student",
        [
            {"fieldname": "display_name", "label": "Display Name", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "guardian_email",
                "label": "Guardian Email",
                "fieldtype": "Data",
                "options": "Email",
            },
            {
                "fieldname": "qr_identifier",
                "label": "QR Identifier",
                "fieldtype": "Data",
                "unique": 1,
                "reqd": 1,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Active\nInactive\nGraduated",
                "default": "Active",
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Group",
        [
            {"fieldname": "group_name", "label": "Group Name", "fieldtype": "Data", "reqd": 1},
            {
                "fieldname": "teacher",
                "label": "Teacher",
                "fieldtype": "Link",
                "options": "Education Teacher",
            },
            {"fieldname": "capacity", "label": "Capacity", "fieldtype": "Int"},
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Session",
        [
            {
                "fieldname": "group",
                "label": "Group",
                "fieldtype": "Link",
                "options": "Education Group",
                "reqd": 1,
            },
            {"fieldname": "starts_at", "label": "Starts At", "fieldtype": "Datetime", "reqd": 1},
            {"fieldname": "ends_at", "label": "Ends At", "fieldtype": "Datetime", "reqd": 1},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Scheduled\nOpen\nComplete\nCancelled",
                "default": "Scheduled",
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Enrollment",
        [
            {
                "fieldname": "student",
                "label": "Student",
                "fieldtype": "Link",
                "options": "Education Student",
                "reqd": 1,
            },
            {
                "fieldname": "group",
                "label": "Group",
                "fieldtype": "Link",
                "options": "Education Group",
                "reqd": 1,
            },
            {"fieldname": "enrolled_on", "label": "Enrolled On", "fieldtype": "Date", "reqd": 1},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Pending\nActive\nRejected\nCompleted",
                "default": "Pending",
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Attendance",
        [
            {
                "fieldname": "session",
                "label": "Session",
                "fieldtype": "Link",
                "options": "Education Session",
                "reqd": 1,
            },
            {
                "fieldname": "student",
                "label": "Student",
                "fieldtype": "Link",
                "options": "Education Student",
                "reqd": 1,
            },
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Present\nAbsent\nLate\nExcused",
                "reqd": 1,
            },
            {
                "fieldname": "recorded_by",
                "label": "Recorded By",
                "fieldtype": "Link",
                "options": "User",
                "read_only": 1,
            },
        ],
        ROLES,
    ),
    operational_schema(
        "Noxus Education",
        "Education Subscription",
        [
            {
                "fieldname": "student",
                "label": "Student",
                "fieldtype": "Link",
                "options": "Education Student",
                "reqd": 1,
            },
            {"fieldname": "label", "label": "Plan Label", "fieldtype": "Data", "reqd": 1},
            {"fieldname": "starts_on", "label": "Starts On", "fieldtype": "Date", "reqd": 1},
            {"fieldname": "ends_on", "label": "Ends On", "fieldtype": "Date"},
            {
                "fieldname": "status",
                "label": "Status",
                "fieldtype": "Select",
                "options": "Active\nPaused\nExpired",
                "default": "Active",
            },
            {
                "fieldname": "billing_enforced",
                "label": "Billing Enforced",
                "fieldtype": "Check",
                "read_only": 1,
                "default": "0",
                "description": "Descriptive only in Community v1",
            },
        ],
        ROLES,
    ),
]
