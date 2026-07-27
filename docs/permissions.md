# Permissions and tenant isolation

Frappe roles and DocType permissions are the authoritative enforcement layer; UI visibility is never
authorization. APIs call `check_permission`, `has_permission(..., throw=True)`, or permission-aware
`frappe.get_list`. Audit access has a permission query condition. Credentials and webhook signing
secrets use Frappe Password fields.

Each tenant has a distinct Frappe site and MariaDB database. The reverse proxy accepts only configured
site hosts. Isolation acceptance creates two real sites, writes the same normalized identifier in
both, authenticates separate users, and verifies API/resource queries never cross databases. Any new
API must include object-level authorization and an IDOR regression test.
