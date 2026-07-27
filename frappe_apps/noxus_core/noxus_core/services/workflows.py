from __future__ import annotations

import json


def install_workflows(workflow_names: list[str]) -> list[str]:
    import frappe

    installed: list[str] = []
    for name in workflow_names:
        template = frappe.db.get_value(
            "Workflow Template",
            {"normalized_id": name},
            ["document_type", "states_json", "transitions_json"],
            as_dict=True,
        )
        if not template:
            frappe.throw(f"Unknown workflow template: {name}")
        states = json.loads(template.states_json)
        transitions = json.loads(template.transitions_json)
        if not frappe.db.exists("Workflow", name):
            doc = frappe.get_doc(
                {
                    "doctype": "Workflow",
                    "workflow_name": name,
                    "document_type": template.document_type,
                    "is_active": 1,
                    "workflow_state_field": "status",
                }
            )
            for state in states:
                doc.append("states", state)
            for transition in transitions:
                doc.append("transitions", transition)
            doc.insert(ignore_permissions=True)
        installed.append(name)
    return installed
