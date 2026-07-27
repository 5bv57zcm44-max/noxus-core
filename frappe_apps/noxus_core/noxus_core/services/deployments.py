from __future__ import annotations

import json
import secrets
from typing import Any

from noxus_core.contracts import BlueprintRequest, ResumeRequest


def status(deployment: str) -> dict[str, Any]:
    import frappe

    document = frappe.get_doc("Deployment Record", deployment)
    document.check_permission("read")
    return {
        "deployment": document.name,
        "blueprint": document.blueprint,
        "stage": document.stage,
        "attempts": document.attempts,
        "error_summary": document.error_summary,
        "modified": document.modified,
    }


def resume(request: ResumeRequest) -> dict[str, str]:
    import frappe

    deployment = frappe.get_doc("Deployment Record", request.deployment)
    deployment.check_permission("write")
    stored_token = deployment.get_password("resume_token")
    if not stored_token or not secrets.compare_digest(stored_token, request.resume_token):
        frappe.throw("Invalid deployment resume token", frappe.AuthenticationError)
    if deployment.stage != "Failed":
        frappe.throw("Only failed deployments can be resumed", frappe.ValidationError)
    blueprint_json = frappe.db.get_value(
        "Solution Blueprint", deployment.blueprint, "blueprint_json"
    )
    blueprint = BlueprintRequest.model_validate(json.loads(blueprint_json))
    deployment.stage = "Queued"
    deployment.error_summary = None
    deployment.attempts = (deployment.attempts or 0) + 1
    deployment.save()
    frappe.enqueue(
        "noxus_core.services.blueprints.apply_background",
        queue="long",
        job_name=f"noxus-blueprint-{deployment.name}-attempt-{deployment.attempts}",
        deployment=deployment.name,
        blueprint=blueprint.model_dump(mode="json"),
        enqueue_after_commit=True,
    )
    return {"deployment": deployment.name, "stage": "Queued"}
