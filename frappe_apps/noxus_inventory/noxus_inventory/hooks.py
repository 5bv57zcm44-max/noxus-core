app_name = "noxus_inventory"
app_title = "NOXUS Inventory"
app_publisher = "NOXUS AI"
app_license = "GPL-3.0-or-later"
after_install = "noxus_inventory.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    "Noxus Item": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Warehouse": {"validate": "noxus_core.module_runtime.validate_record"},
    "Noxus Stock Movement": {"validate": "noxus_core.module_runtime.validate_record"},
}
