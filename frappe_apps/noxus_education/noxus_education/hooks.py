app_name = "noxus_education"
app_title = "NOXUS Education"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_education.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    doctype: {"validate": "noxus_core.module_runtime.validate_record"}
    for doctype in [
        "Education Teacher",
        "Education Student",
        "Education Group",
        "Education Session",
        "Education Enrollment",
        "Education Attendance",
        "Education Subscription",
    ]
}
