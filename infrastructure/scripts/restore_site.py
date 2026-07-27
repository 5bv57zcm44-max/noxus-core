"""Restore a Frappe site without exposing database credentials in argv."""

from __future__ import annotations

import os
from pathlib import Path

import frappe
from frappe.commands.site import _restore
from frappe.utils.synchronization import filelock


def read_secret(value_name: str, file_name: str) -> str:
    value = os.environ.get(value_name, "").strip()
    if not value:
        secret_path = os.environ.get(file_name, "")
        if secret_path:
            value = Path(secret_path).read_text(encoding="utf-8").strip()
    if not value:
        raise SystemExit(f"{value_name} or {file_name} must provide a non-empty secret")
    return value


def main() -> None:
    site = os.environ.get("NOXUS_SITE", "").strip().lower()
    backup = Path(os.environ.get("NOXUS_BACKUP_PATH", "")).resolve()
    if not site or not (Path("sites") / site / "site_config.json").is_file():
        raise SystemExit("NOXUS_SITE must identify an existing site")
    if not backup.is_file():
        raise SystemExit("NOXUS_BACKUP_PATH must identify the mounted backup file")

    root_password = read_secret("MARIADB_ROOT_PASSWORD", "MARIADB_ROOT_PASSWORD_FILE")
    frappe.init(site)
    with filelock("site_restore", timeout=1):
        _restore(
            site=site,
            sql_file_path=str(backup),
            db_root_username="root",
            db_root_password=root_password,
        )


if __name__ == "__main__":
    main()
