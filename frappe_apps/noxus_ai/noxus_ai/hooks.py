app_name = "noxus_ai"
app_title = "NOXUS AI"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_ai.install.after_install"
required_apps = ["noxus_core"]
doc_events = {"AI Provider Configuration": {"validate": "noxus_ai.service.validate_provider"}}
