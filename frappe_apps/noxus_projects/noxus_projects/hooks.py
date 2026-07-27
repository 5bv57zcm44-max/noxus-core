app_name = "noxus_projects"
app_title = "NOXUS Projects"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_projects.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    "Noxus Project": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Task": {"validate": "noxus_core.module_runtime.validate_record"},
}
