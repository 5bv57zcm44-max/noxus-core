from __future__ import annotations


def preflight() -> dict[str, object]:
    import frappe

    return {
        "site": frappe.local.site,
        "scheduler_enabled": not bool(frappe.conf.pause_scheduler),
        "pending_jobs": frappe.db.count("RQ Job", {"status": ["in", ["queued", "started"]]}),
        "backup_required": True,
        "strategy": "build new image, back up, migrate, health-check, retain previous image",
    }


def record_upgrade_status() -> None:
    from noxus_core.services.audit import record_event

    record_event("upgrade.preflight", "Site", "current", preflight())
