from noxus_core.schema import CORE_SCHEMAS as _CORE_SCHEMAS

app_name = "noxus_core"
app_title = "NOXUS Core"
app_publisher = "NOXUS AI"
app_description = "Modular solution control plane"
app_email = "security@noxus.example"
app_license = "GPL-3.0-or-later"
app_version = "1.0.0"

after_install = "noxus_core.install.after_install"
before_uninstall = "noxus_core.install.before_uninstall"
has_permission = {
    definition["name"]: "noxus_core.permissions.has_permission" for definition in _CORE_SCHEMAS
}
permission_query_conditions = {"Audit Event": "noxus_core.permissions.audit_query"}
doc_events = {
    "Audit Event": {
        "validate": "noxus_core.services.audit.reject_audit_mutation",
        "before_update_after_submit": "noxus_core.services.audit.reject_audit_mutation",
        "on_trash": "noxus_core.services.audit.reject_audit_mutation",
    },
    "API Credential": {"validate": "noxus_core.services.integrations.validate_credential"},
    "Webhook Endpoint": {"validate": "noxus_core.services.integrations.validate_webhook"},
}
scheduler_events = {
    "hourly": ["noxus_core.services.health.run_scheduled_checks"],
    "daily": ["noxus_core.services.upgrades.record_upgrade_status"],
}
