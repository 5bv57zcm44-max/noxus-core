app_name = "noxus_maintenance"
app_title = "NOXUS Maintenance"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_maintenance.install.after_install"
required_apps = ["noxus_core", "noxus_inventory"]
doc_events = {
    doctype: {"validate": "noxus_core.module_runtime.validate_record"}
    for doctype in [
        "Maintenance Asset",
        "Maintenance Request",
        "Maintenance Work Order",
        "Maintenance Technician",
        "Preventive Maintenance Schedule",
        "Spare Part Requirement",
        "Maintenance Attachment",
    ]
}
