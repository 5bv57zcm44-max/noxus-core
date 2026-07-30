import frappe
from frappe.tests.utils import FrappeTestCase

from noxus_core.contracts import BlueprintRequest


class TestNoxusPermissions(FrappeTestCase):
    def _user(self, email: str, roles: list[str]) -> str:
        if not frappe.db.exists("User", email):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": email,
                    "first_name": "NOXUS Test",
                    "send_welcome_email": 0,
                    "roles": [{"role": role} for role in roles],
                }
            ).insert(ignore_permissions=True)
        return email

    def test_auditor_cannot_mutate_audit_event(self):
        from noxus_core.services.audit import record_event

        name = record_event("test.created", "Test", "one")
        user = "noxus-auditor@example.test"
        if not frappe.db.exists("User", user):
            frappe.get_doc(
                {
                    "doctype": "User",
                    "email": user,
                    "first_name": "Auditor",
                    "roles": [{"role": "Noxus Auditor"}],
                }
            ).insert(ignore_permissions=True)
        frappe.set_user(user)
        event = frappe.get_doc("Audit Event", name)
        self.assertTrue(event.has_permission("read"))
        event.action = "tampered"
        self.assertRaises(frappe.PermissionError, event.save)

    def test_guest_cannot_read_the_module_catalog(self):
        from noxus_core.api.v1 import catalog

        frappe.set_user("Guest")
        self.assertRaises(frappe.PermissionError, catalog)

    def test_unknown_workflow_and_arbitrary_automation_are_rejected(self):
        from noxus_core.services.automation import execute
        from noxus_core.services.workflows import install_workflows

        self.assertRaises(frappe.ValidationError, install_workflows, ["not-a-workflow"])
        self.assertRaises(
            frappe.ValidationError,
            execute,
            "Run Python",
            {"code": "raise SystemExit"},
            object(),
        )

    def test_blueprint_checksum_is_verified_before_application(self):
        from noxus_core.services.blueprints import verify_blueprint

        blueprint = BlueprintRequest.model_validate(
            {
                "schema_version": 1,
                "name": "invalid-checksum",
                "industry": "general-business",
                "modules": [],
                "generator_version": "1.0.0",
                "checksum": "0" * 64,
            }
        )
        self.assertRaises(ValueError, verify_blueprint, blueprint)

    def test_support_workflow_enforces_permissions_and_transitions(self):
        from noxus_support.api.v1 import transition_ticket

        ticket_id = f"acceptance.permission-ticket.{frappe.generate_hash(length=8).lower()}"
        ticket = frappe.get_doc(
            {
                "doctype": "Noxus Support Ticket",
                "normalized_id": ticket_id,
                "subject": "Permission boundary",
                "description": "Container acceptance test",
                "status": "Open",
            }
        ).insert(ignore_permissions=True)

        frappe.set_user(self._user("noxus-unprivileged@example.test", []))
        self.assertRaises(
            frappe.PermissionError,
            transition_ticket,
            ticket.name,
            "In Progress",
        )

        frappe.set_user("Administrator")
        manager = self._user("noxus-support-manager@example.test", ["Support Manager"])
        frappe.set_user(manager)
        result = transition_ticket(ticket.name, "In Progress")
        self.assertEqual(result["status"], "In Progress")
        self.assertRaises(frappe.ValidationError, transition_ticket, ticket.name, "Open")

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()
