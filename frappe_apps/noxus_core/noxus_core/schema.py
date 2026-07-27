from __future__ import annotations

from typing import Any

AUDIT_FIELDS = [
    {
        "fieldname": "normalized_id",
        "label": "Normalized ID",
        "fieldtype": "Data",
        "unique": 1,
        "reqd": 1,
    },
    {
        "fieldname": "schema_version",
        "label": "Schema Version",
        "fieldtype": "Int",
        "default": "1",
        "reqd": 1,
    },
    {"fieldname": "checksum", "label": "Checksum", "fieldtype": "Data", "read_only": 1},
    {
        "fieldname": "lifecycle_state",
        "label": "Lifecycle State",
        "fieldtype": "Select",
        "options": "Draft\nActive\nDisabled\nArchived",
        "default": "Draft",
    },
]


def field(fieldname: str, label: str, fieldtype: str = "Data", **extra: Any) -> dict[str, Any]:
    return {"fieldname": fieldname, "label": label, "fieldtype": fieldtype, **extra}


def schema(
    name: str,
    fields: list[dict[str, Any]],
    *,
    permissions: list[dict[str, Any]] | None = None,
    autoname: str = "field:normalized_id",
) -> dict[str, Any]:
    return {
        "doctype": "DocType",
        "name": name,
        "module": "Noxus Core",
        "custom": 1,
        "autoname": autoname,
        "track_changes": 1,
        "fields": fields,
        "permissions": permissions
        or [
            {
                "role": "Noxus Administrator",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "export": 1,
            },
            {"role": "Noxus Auditor", "read": 1, "export": 1},
        ],
    }


CORE_SCHEMAS = [
    schema(
        "Noxus Module",
        [
            *AUDIT_FIELDS,
            field("display_name", "Display Name", reqd=1),
            field("description", "Description", "Text Editor"),
            field("publisher", "Publisher"),
            field("license", "License"),
            field("category", "Category"),
            field("manifest_json", "Manifest", "JSON", reqd=1),
        ],
    ),
    schema(
        "Module Version",
        [
            *AUDIT_FIELDS,
            field("module", "Module", "Link", options="Noxus Module", reqd=1),
            field("version", "Version", reqd=1),
            field("released_at", "Released At", "Datetime"),
            field("platform_constraints", "Platform Constraints", "JSON"),
        ],
    ),
    schema(
        "Module Dependency",
        [
            *AUDIT_FIELDS,
            field("module", "Module", "Link", options="Noxus Module", reqd=1),
            field("dependency", "Dependency", "Data", reqd=1),
            field("constraint", "Constraint"),
            field(
                "dependency_type",
                "Dependency Type",
                "Select",
                options="Required\nRecommended\nConflict",
                reqd=1,
            ),
        ],
    ),
    schema(
        "Installed Module",
        [
            *AUDIT_FIELDS,
            field("module", "Module", "Link", options="Noxus Module", reqd=1),
            field("installed_version", "Installed Version", reqd=1),
            field("installed_at", "Installed At", "Datetime"),
            field(
                "migration_state", "Migration State", "Select", options="Current\nPending\nFailed"
            ),
        ],
    ),
    schema(
        "Feature Definition",
        [
            *AUDIT_FIELDS,
            field("module", "Module", "Link", options="Noxus Module"),
            field("feature_key", "Feature Key", reqd=1),
            field("description", "Description", "Text"),
        ],
    ),
    schema(
        "Feature Flag",
        [
            *AUDIT_FIELDS,
            field("feature", "Feature", "Link", options="Feature Definition", reqd=1),
            field("enabled", "Enabled", "Check"),
            field("scope", "Scope", "Select", options="Site\nUser\nRole", default="Site"),
            field("scope_value", "Scope Value"),
        ],
    ),
    schema(
        "Industry Template",
        [
            *AUDIT_FIELDS,
            field("industry", "Industry", reqd=1),
            field("blueprint_json", "Blueprint", "JSON", reqd=1),
        ],
    ),
    schema(
        "Solution Blueprint",
        [
            *AUDIT_FIELDS,
            field("industry", "Industry", reqd=1),
            field("blueprint_json", "Blueprint", "JSON", reqd=1),
            field("generator_version", "Generator Version", reqd=1),
            field("applied_at", "Applied At", "Datetime"),
        ],
    ),
    schema(
        "Solution Blueprint Module",
        [
            *AUDIT_FIELDS,
            field("blueprint", "Blueprint", "Link", options="Solution Blueprint", reqd=1),
            field("module", "Module", "Data", reqd=1),
            field("version", "Version", reqd=1),
            field("install_order", "Install Order", "Int", reqd=1),
            field("features", "Features", "JSON"),
        ],
    ),
    schema(
        "Workspace Configuration",
        [
            *AUDIT_FIELDS,
            field("workspace_key", "Workspace Key", reqd=1),
            field("configuration", "Configuration", "JSON", reqd=1),
        ],
    ),
    schema(
        "Role Template",
        [
            *AUDIT_FIELDS,
            field("role_name", "Role Name", reqd=1),
            field("permissions_json", "Permissions", "JSON", reqd=1),
        ],
    ),
    schema(
        "Permission Template",
        [
            *AUDIT_FIELDS,
            field("permission_key", "Permission Key", reqd=1),
            field("rules_json", "Rules", "JSON", reqd=1),
        ],
    ),
    schema(
        "Workflow Template",
        [
            *AUDIT_FIELDS,
            field("document_type", "Document Type", reqd=1),
            field("states_json", "States", "JSON", reqd=1),
            field("transitions_json", "Transitions", "JSON", reqd=1),
        ],
    ),
    schema(
        "Automation Rule",
        [
            *AUDIT_FIELDS,
            field("event", "Event", reqd=1),
            field(
                "action_type",
                "Action Type",
                "Select",
                options="Notification\nAssignment\nField Change\nCreate Document\nSigned Webhook",
                reqd=1,
            ),
            field("action_config", "Action Configuration", "JSON", reqd=1),
            field("enabled", "Enabled", "Check"),
        ],
    ),
    schema(
        "Integration Definition",
        [
            *AUDIT_FIELDS,
            field("provider", "Provider", reqd=1),
            field("endpoint_allowlist", "Endpoint Allow-list", "Small Text"),
            field("timeout_seconds", "Timeout Seconds", "Int", default="10"),
        ],
    ),
    schema(
        "Webhook Endpoint",
        [
            *AUDIT_FIELDS,
            field("url", "URL", reqd=1),
            field("events", "Events", "JSON", reqd=1),
            field("signing_secret", "Signing Secret", "Password", reqd=1),
            field("enabled", "Enabled", "Check"),
        ],
    ),
    schema(
        "API Credential",
        [
            *AUDIT_FIELDS,
            field("provider", "Provider", reqd=1),
            field("credential", "Credential", "Password", reqd=1),
            field("expires_at", "Expires At", "Datetime"),
            field("last_four", "Last Four", read_only=1),
        ],
    ),
    schema(
        "Audit Event",
        [
            field("normalized_id", "Normalized ID", reqd=1, unique=1),
            field("occurred_at", "Occurred At", "Datetime", reqd=1),
            field("actor", "Actor", "Link", options="User"),
            field("action", "Action", reqd=1),
            field("subject_type", "Subject Type", reqd=1),
            field("subject_id", "Subject ID", reqd=1),
            field("payload", "Payload", "JSON"),
            field("checksum", "Checksum", read_only=1),
        ],
        permissions=[
            {"role": "Noxus Auditor", "read": 1, "export": 1},
            {"role": "System Manager", "read": 1, "export": 1},
        ],
        autoname="field:normalized_id",
    ),
    schema(
        "Deployment Record",
        [
            *AUDIT_FIELDS,
            field("blueprint", "Blueprint", "Link", options="Solution Blueprint"),
            field("idempotency_key", "Idempotency Key", reqd=1, unique=1),
            field(
                "stage",
                "Stage",
                "Select",
                options="Queued\nLocked\nValidating\nInstalling\nMigrating\nComplete\nFailed",
                reqd=1,
            ),
            field("resume_token", "Resume Token", "Password"),
            field("error_summary", "Error Summary", "Small Text"),
            field("previous_image", "Previous Image"),
            field("target_image", "Target Image"),
            field("attempts", "Attempts", "Int", default="0", read_only=1),
        ],
    ),
    schema(
        "System Health Check",
        [
            *AUDIT_FIELDS,
            field("check_name", "Check Name", reqd=1),
            field("status", "Status", "Select", options="Healthy\nDegraded\nFailed", reqd=1),
            field("checked_at", "Checked At", "Datetime", reqd=1),
            field("details", "Details", "JSON"),
        ],
    ),
    schema(
        "Tenant Branding",
        [
            *AUDIT_FIELDS,
            field("product_name", "Product Name", reqd=1),
            field("accent_color", "Accent Color", "Color"),
            field("logo", "Logo", "Attach Image"),
            field("default_direction", "Default Direction", "Select", options="LTR\nRTL"),
        ],
    ),
    schema(
        "Subscription Metadata",
        [
            *AUDIT_FIELDS,
            field("plan_label", "Plan Label"),
            field("valid_until", "Valid Until", "Date"),
            field("metadata", "Metadata", "JSON"),
            field("enforcement_enabled", "Enforcement Enabled", "Check", read_only=1, default="0"),
        ],
    ),
]
