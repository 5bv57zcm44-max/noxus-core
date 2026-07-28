"""Create a Frappe site without placing credentials in process arguments."""

from __future__ import annotations

import os
import re
from pathlib import Path

import frappe
from frappe.installer import _new_site

SITE_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(?:\.(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?))*$"
)


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
    if not SITE_PATTERN.fullmatch(site):
        raise SystemExit("NOXUS_SITE must be a valid lowercase DNS hostname")

    admin_password = read_secret("NOXUS_ADMIN_PASSWORD", "NOXUS_ADMIN_PASSWORD_FILE")
    root_password = read_secret("MARIADB_ROOT_PASSWORD", "MARIADB_ROOT_PASSWORD_FILE")

    bench_root = Path(os.environ.get("FRAPPE_BENCH_ROOT", "/home/frappe/frappe-bench")).resolve()
    sites_path = bench_root / "sites"
    if not sites_path.is_dir():
        raise SystemExit(f"Frappe sites directory does not exist: {sites_path}")
    os.chdir(sites_path)
    frappe.init(site, new_site=True)
    _new_site(
        None,
        site,
        db_root_username="root",
        db_root_password=root_password,
        admin_password=admin_password,
        db_type="mariadb",
        db_host=os.environ.get("MARIADB_HOST", "mariadb"),
        db_port=int(os.environ.get("MARIADB_PORT", "3306")),
        mariadb_user_host_login_scope="%",
    )


if __name__ == "__main__":
    main()
