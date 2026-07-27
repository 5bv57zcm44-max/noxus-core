from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def installed_manifests() -> list[dict[str, Any]]:
    import frappe

    manifests: list[dict[str, Any]] = []
    for app in frappe.get_installed_apps():
        path = Path(frappe.get_app_path(app)).parent / "noxus-module.yml"
        if path.is_file():
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                manifests.append(raw)
    return sorted(manifests, key=lambda item: str(item["name"]))


def synchronize_registry() -> list[str]:
    import frappe

    synchronized: list[str] = []
    for manifest in installed_manifests():
        normalized = str(manifest["name"])
        body = json.dumps(manifest, sort_keys=True)
        values = {
            "display_name": manifest["display_name"],
            "description": manifest["description"],
            "publisher": manifest["publisher"],
            "license": manifest["license"],
            "category": manifest["category"],
            "manifest_json": body,
            "checksum": hashlib.sha256(body.encode()).hexdigest(),
            "lifecycle_state": "Active",
        }
        if frappe.db.exists("Noxus Module", normalized):
            frappe.db.set_value("Noxus Module", normalized, values, update_modified=False)
        else:
            frappe.get_doc(
                {"doctype": "Noxus Module", "normalized_id": normalized, **values}
            ).insert(ignore_permissions=True)
        synchronized.append(normalized)
        installed_values = {
            "module": normalized,
            "installed_version": manifest["version"],
            "installed_at": frappe.utils.now_datetime(),
            "migration_state": "Current",
            "lifecycle_state": "Active",
            "checksum": hashlib.sha256(body.encode()).hexdigest(),
        }
        if frappe.db.exists("Installed Module", normalized):
            frappe.db.set_value(
                "Installed Module", normalized, installed_values, update_modified=False
            )
        else:
            frappe.get_doc(
                {
                    "doctype": "Installed Module",
                    "normalized_id": normalized,
                    **installed_values,
                }
            ).insert(ignore_permissions=True)
    return synchronized
