app_name = "noxus_transport"
app_title = "NOXUS Transport"
app_publisher = "NOXUS AI"
app_description = "Vehicles, drivers, trips, and passenger workflows for NOXUS"
app_email = "security@noxus.example"
app_license = "GPL-3.0-or-later"
app_version = "1.0.0rc1"
after_install = "noxus_transport.install.after_install"
required_apps = ["noxus_core"]
doc_events = {
    doctype: {"validate": "noxus_core.module_runtime.validate_record"}
    for doctype in [
        "Transport Vehicle",
        "Transport Driver",
        "Transport Trip",
        "Transport Stop",
        "Passenger Manifest",
        "Vehicle Document",
        "Driver Document",
        "Transport Location Event",
    ]
}
