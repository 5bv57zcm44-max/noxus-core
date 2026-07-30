app_name = "noxus_projects"
app_title = "NOXUS Projects"
app_publisher = "NOXUS AI"
app_description = "Standalone project and task management for NOXUS"
app_email = "security@noxus.example"
app_license = "GPL-3.0-or-later"
app_version = "1.0.0"
after_install = "noxus_projects.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    "Noxus Project": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Task": {"validate": "noxus_core.module_runtime.validate_record"},
}
