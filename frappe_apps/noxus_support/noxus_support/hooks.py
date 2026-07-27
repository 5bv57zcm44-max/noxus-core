app_name = "noxus_support"
app_title = "NOXUS Support"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_support.install.after_install"
required_apps = ["noxus_core"]
doc_events = {"Noxus Support Ticket": {"validate": "noxus_core.module_runtime.validate_record"}}
