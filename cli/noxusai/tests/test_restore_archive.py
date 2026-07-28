from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from infrastructure.scripts.restore_site import prepared_database_backup


def test_stages_gzip_database_backup_privately(tmp_path: Path) -> None:
    backup = tmp_path / "database.sql.gz"
    contents = b"-- MariaDB dump\nCREATE TABLE test (id int);\n"
    with gzip.open(backup, "wb") as archive:
        archive.write(contents)

    with prepared_database_backup(backup) as prepared:
        assert prepared != backup
        assert prepared.read_bytes() == contents
        staged_path = prepared

    assert backup.is_file()
    assert not staged_path.exists()


def test_preserves_uncompressed_database_backup(tmp_path: Path) -> None:
    backup = tmp_path / "database.sql"
    backup.write_text("-- MariaDB dump\n", encoding="utf-8")

    with prepared_database_backup(backup) as prepared:
        assert prepared == backup

    assert backup.is_file()


def test_rejects_corrupt_gzip_database_backup(tmp_path: Path) -> None:
    backup = tmp_path / "database.sql.gz"
    backup.write_bytes(b"\x1f\x8bnot-a-valid-archive")

    with pytest.raises(SystemExit, match="not a valid gzip database backup"):
        with prepared_database_backup(backup):
            pass


def test_does_not_relabel_restore_failures_as_archive_failures(tmp_path: Path) -> None:
    backup = tmp_path / "database.sql.gz"
    with gzip.open(backup, "wb") as archive:
        archive.write(b"-- MariaDB dump\n")

    with pytest.raises(RuntimeError, match="restore failed"):
        with prepared_database_backup(backup) as prepared:
            staged_path = prepared
            raise RuntimeError("restore failed")

    assert not staged_path.exists()
