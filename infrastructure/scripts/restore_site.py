"""Restore a Frappe site without exposing database credentials in argv."""

from __future__ import annotations

import gzip
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def read_secret(value_name: str, file_name: str) -> str:
    value = os.environ.get(value_name, "").strip()
    if not value:
        secret_path = os.environ.get(file_name, "")
        if secret_path:
            value = Path(secret_path).read_text(encoding="utf-8").strip()
    if not value:
        raise SystemExit(f"{value_name} or {file_name} must provide a non-empty secret")
    return value


@contextmanager
def prepared_database_backup(backup: Path) -> Iterator[Path]:
    """Yield an uncompressed SQL backup and remove any private staging file."""

    with backup.open("rb") as source:
        is_gzip = source.read(2) == b"\x1f\x8b"
    if not is_gzip:
        yield backup
        return

    with tempfile.TemporaryDirectory(prefix="noxus-restore-") as temporary_directory:
        staged_backup = Path(temporary_directory) / "database.sql"
        try:
            descriptor = os.open(
                staged_backup,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
            with gzip.open(backup, "rb") as source, os.fdopen(descriptor, "wb") as destination:
                shutil.copyfileobj(source, destination, length=1024 * 1024)
        except (gzip.BadGzipFile, EOFError, OSError) as exc:
            raise SystemExit("NOXUS_BACKUP_PATH is not a valid gzip database backup") from exc
        yield staged_backup


def main() -> None:
    import frappe
    from frappe.commands.site import _restore
    from frappe.utils.synchronization import filelock

    site = os.environ.get("NOXUS_SITE", "").strip().lower()
    backup = Path(os.environ.get("NOXUS_BACKUP_PATH", "")).resolve()
    bench_root = Path(os.environ.get("FRAPPE_BENCH_ROOT", "/home/frappe/frappe-bench")).resolve()
    sites_path = bench_root / "sites"
    if not site or not (sites_path / site / "site_config.json").is_file():
        raise SystemExit("NOXUS_SITE must identify an existing site")
    if not backup.is_file():
        raise SystemExit("NOXUS_BACKUP_PATH must identify the mounted backup file")

    root_password = read_secret("MARIADB_ROOT_PASSWORD", "MARIADB_ROOT_PASSWORD_FILE")
    os.chdir(sites_path)
    frappe.init(site)
    with prepared_database_backup(backup) as sql_backup:
        with filelock("site_restore", timeout=1):
            _restore(
                site=site,
                sql_file_path=str(sql_backup),
                db_root_username="root",
                db_root_password=root_password,
            )


if __name__ == "__main__":
    main()
