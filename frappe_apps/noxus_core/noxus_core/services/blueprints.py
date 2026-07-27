from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any

from noxus_core.contracts import ApplyRequest, BlueprintRequest


def verify_blueprint(blueprint: BlueprintRequest) -> None:
    body = blueprint.model_dump(mode="json")
    supplied = body.pop("checksum")
    expected = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if not secrets.compare_digest(supplied, expected):
        raise ValueError("Blueprint checksum is invalid")


def queue_application(request: ApplyRequest) -> dict[str, str]:
    import frappe

    verify_blueprint(request.blueprint)
    existing = frappe.db.get_value(
        "Deployment Record",
        {"idempotency_key": request.idempotency_key},
        ["name", "stage"],
        as_dict=True,
    )
    if existing:
        return {"deployment": existing.name, "stage": existing.stage, "idempotent": "true"}
    blueprint_json = json.dumps(
        request.blueprint.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    blueprint_name = request.blueprint.name
    existing_blueprint = frappe.db.get_value(
        "Solution Blueprint", blueprint_name, ["name", "checksum"], as_dict=True
    )
    if existing_blueprint and existing_blueprint.checksum != request.blueprint.checksum:
        frappe.throw(
            "A blueprint with this identifier already exists with a different checksum",
            frappe.DuplicateEntryError,
        )
    if not existing_blueprint:
        frappe.get_doc(
            {
                "doctype": "Solution Blueprint",
                "normalized_id": blueprint_name,
                "industry": request.blueprint.industry,
                "blueprint_json": blueprint_json,
                "generator_version": request.blueprint.generator_version,
                "checksum": request.blueprint.checksum,
                "lifecycle_state": "Draft",
            }
        ).insert()
        for module in request.blueprint.modules:
            module_digest = hashlib.sha256(
                f"{blueprint_name}:{module.install_order}:{module.name}".encode()
            ).hexdigest()[:12]
            module_id = (
                f"{blueprint_name[:60]}.{module.install_order}.{module.name[:50]}.{module_digest}"
            )
            frappe.get_doc(
                {
                    "doctype": "Solution Blueprint Module",
                    "normalized_id": module_id,
                    "blueprint": blueprint_name,
                    "module": module.name,
                    "version": module.version,
                    "install_order": module.install_order,
                    "features": json.dumps(module.features, sort_keys=True),
                    "lifecycle_state": "Active",
                }
            ).insert()
    deployment = frappe.get_doc(
        {
            "doctype": "Deployment Record",
            "normalized_id": request.idempotency_key,
            "idempotency_key": request.idempotency_key,
            "stage": "Queued",
            "lifecycle_state": "Active",
            "resume_token": secrets.token_urlsafe(32),
            "checksum": request.blueprint.checksum,
            "blueprint": blueprint_name,
            "attempts": 1,
        }
    ).insert()
    frappe.enqueue(
        "noxus_core.services.blueprints.apply_background",
        queue="long",
        job_name=f"noxus-blueprint-{deployment.name}",
        deployment=deployment.name,
        blueprint=request.blueprint.model_dump(mode="json"),
        enqueue_after_commit=True,
    )
    return {"deployment": deployment.name, "stage": "Queued", "idempotent": "false"}


def _set_stage(deployment: str, stage: str, error: str | None = None) -> None:
    import frappe

    values: dict[str, Any] = {"stage": stage}
    if error:
        values["error_summary"] = error[:2000]
    frappe.db.set_value("Deployment Record", deployment, values, update_modified=True)
    frappe.db.commit()


def apply_background(deployment: str, blueprint: dict[str, Any]) -> None:
    import frappe

    from noxus_core.services.audit import record_event
    from noxus_core.services.roles import install_roles
    from noxus_core.services.workflows import install_workflows

    lock = frappe.cache.lock(f"noxus:blueprint:{frappe.local.site}", timeout=900)
    if not lock.acquire(blocking=False):
        _set_stage(deployment, "Failed", "Another blueprint operation holds the site lock")
        return
    try:
        _set_stage(deployment, "Locked")
        request = BlueprintRequest.model_validate(blueprint)
        verify_blueprint(request)
        _set_stage(deployment, "Validating")
        _set_stage(deployment, "Installing")
        from frappe.installer import install_app

        for module in sorted(request.modules, key=lambda item: item.install_order):
            if module.name not in frappe.get_installed_apps():
                install_app(module.name)
        install_roles(request.roles)
        install_workflows(request.workflows)
        _set_stage(deployment, "Migrating")
        from frappe.migrate import SiteMigration

        SiteMigration().run(site=frappe.local.site)
        _set_stage(deployment, "Complete")
        frappe.db.set_value(
            "Solution Blueprint",
            request.name,
            {"lifecycle_state": "Active", "applied_at": frappe.utils.now_datetime()},
            update_modified=True,
        )
        record_event(
            "blueprint.applied", "Deployment Record", deployment, {"blueprint": request.name}
        )
    except Exception as exc:
        _set_stage(deployment, "Failed", str(exc))
        record_event("blueprint.failed", "Deployment Record", deployment, {"error": str(exc)})
        raise
    finally:
        lock.release()
