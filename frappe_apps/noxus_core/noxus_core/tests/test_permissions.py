import frappe
from frappe.tests.utils import FrappeTestCase


class TestNoxusPermissions(FrappeTestCase):
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

    def tearDown(self):
        frappe.set_user("Administrator")
        super().tearDown()
