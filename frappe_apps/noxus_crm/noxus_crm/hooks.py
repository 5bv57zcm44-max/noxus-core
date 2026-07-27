app_name = "noxus_crm"
app_title = "NOXUS CRM"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_crm.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    "Noxus Lead": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Opportunity": {"validate": "noxus_core.module_runtime.validate_record"},
}
