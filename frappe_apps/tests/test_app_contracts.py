import importlib
import sys
from pathlib import Path

import yaml
from noxus_module_sdk.manifest import ModuleManifest
from noxus_module_sdk.resolver import DependencyResolver

APP_ROOT = Path(__file__).resolve().parents[1]
APPS = {
    "noxus_core",
    "noxus_crm",
    "noxus_inventory",
    "noxus_projects",
    "noxus_support",
    "noxus_maintenance",
    "noxus_transport",
    "noxus_education",
    "noxus_ai",
}


def _prepare_imports() -> None:
    for app in sorted(APPS):
        path = str(APP_ROOT / app)
        if path not in sys.path:
            sys.path.insert(0, path)


def test_every_frappe_app_has_a_valid_resolvable_manifest() -> None:
    manifests = []
    for app in APPS:
        raw = yaml.safe_load((APP_ROOT / app / "noxus-module.yml").read_text(encoding="utf-8"))
        manifests.append(ModuleManifest.model_validate(raw))
    result = DependencyResolver(manifests).resolve(sorted(APPS))
    order = [item.name for item in result.installation_order]
    assert set(order) == APPS
    assert order.index("noxus_inventory") < order.index("noxus_maintenance")


def test_industry_apps_ship_every_required_operational_record() -> None:
    _prepare_imports()
    expected = {
        "noxus_maintenance": {
            "Maintenance Asset",
            "Maintenance Request",
            "Maintenance Work Order",
            "Maintenance Technician",
            "Preventive Maintenance Schedule",
            "Spare Part Requirement",
            "Maintenance Attachment",
        },
        "noxus_transport": {
            "Transport Vehicle",
            "Transport Driver",
            "Transport Trip",
            "Transport Stop",
            "Passenger Manifest",
            "Vehicle Document",
            "Driver Document",
            "Transport Location Event",
        },
        "noxus_education": {
            "Education Teacher",
            "Education Student",
            "Education Group",
            "Education Session",
            "Education Enrollment",
            "Education Attendance",
            "Education Subscription",
        },
    }
    for app, required in expected.items():
        schemas = importlib.import_module(f"{app}.schema").SCHEMAS
        names = {item["name"] for item in schemas}
        assert names == required
        for schema in schemas:
            fields = {field["fieldname"] for field in schema["fields"]}
            assert {"normalized_id", "record_version", "checksum"} <= fields
            assert schema["permissions"]


def test_core_defines_every_public_contract_doctype() -> None:
    _prepare_imports()
    schemas = importlib.import_module("noxus_core.schema").CORE_SCHEMAS
    names = {item["name"] for item in schemas}
    assert {
        "Noxus Module",
        "Module Version",
        "Module Dependency",
        "Installed Module",
        "Feature Definition",
        "Feature Flag",
        "Industry Template",
        "Solution Blueprint",
        "Solution Blueprint Module",
        "Workspace Configuration",
        "Role Template",
        "Permission Template",
        "Workflow Template",
        "Automation Rule",
        "Integration Definition",
        "Webhook Endpoint",
        "API Credential",
        "Audit Event",
        "Deployment Record",
        "System Health Check",
        "Tenant Branding",
        "Subscription Metadata",
    } == names


def test_dynamic_links_point_to_doctype_link_fields() -> None:
    _prepare_imports()
    for app in APPS:
        schema_module = importlib.import_module(f"{app}.schema")
        schemas = getattr(schema_module, "SCHEMAS", getattr(schema_module, "CORE_SCHEMAS", []))
        for schema in schemas:
            fields = {field["fieldname"]: field for field in schema["fields"]}
            for field in fields.values():
                if field["fieldtype"] != "Dynamic Link":
                    continue
                pointer = fields[field["options"]]
                assert pointer["fieldtype"] == "Link"
                assert pointer["options"] == "DocType"


def test_custom_link_targets_exist_before_their_consumers() -> None:
    _prepare_imports()
    manifests = []
    schemas_by_app = {}
    custom_doctypes = set()
    for app in APPS:
        raw = yaml.safe_load((APP_ROOT / app / "noxus-module.yml").read_text(encoding="utf-8"))
        manifests.append(ModuleManifest.model_validate(raw))
        schema_module = importlib.import_module(f"{app}.schema")
        schemas = getattr(schema_module, "SCHEMAS", getattr(schema_module, "CORE_SCHEMAS", []))
        schemas_by_app[app] = schemas
        custom_doctypes.update(schema["name"] for schema in schemas)

    installation_order = DependencyResolver(manifests).resolve(sorted(APPS)).installation_order
    installed_doctypes = set()
    for module in installation_order:
        for schema in schemas_by_app[module.name]:
            for field in schema["fields"]:
                target = field.get("options")
                if field["fieldtype"] == "Link" and target in custom_doctypes:
                    assert target in installed_doctypes, (
                        f"{module.name}.{schema['name']}.{field['fieldname']} references "
                        f"{target} before Frappe creates it"
                    )
            installed_doctypes.add(schema["name"])


def test_webhook_signatures_reject_changes() -> None:
    _prepare_imports()
    from noxus_core.services.webhooks import sign, verify

    signature = sign("secret", b'{"event":"created"}', "1700000000")
    assert verify("secret", b'{"event":"created"}', "1700000000", signature)
    assert not verify("secret", b'{"event":"changed"}', "1700000000", signature)
