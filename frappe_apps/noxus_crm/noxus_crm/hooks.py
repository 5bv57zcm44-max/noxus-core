app_name = "noxus_crm"
app_title = "NOXUS CRM"
app_publisher = "NOXUS AI"
app_description = "Standalone customer relationship management for NOXUS"
app_email = "security@noxus.example"
app_license = "GPL-3.0-or-later"
app_version = "1.0.0"
after_install = "noxus_crm.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    "Noxus Lead": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Opportunity": {"validate": "noxus_core.module_runtime.validate_record"},
}
