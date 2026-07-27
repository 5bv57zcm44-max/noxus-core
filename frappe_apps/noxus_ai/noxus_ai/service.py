from urllib.parse import urlparse


def validate_provider(doc, method: str | None = None) -> None:
    import frappe
    from noxus_core.services.integrations import validate_endpoint

    if doc.status == "Enabled" and not doc.credential:
        frappe.throw("An encrypted credential is required before enabling a provider")
    if not 1 <= int(doc.timeout_seconds) <= 60:
        frappe.throw("Provider timeout must be between 1 and 60 seconds")
    parsed = urlparse(doc.base_url)
    if parsed.hostname != doc.allowed_hostname:
        frappe.throw("Provider URL must match its explicit allowed hostname")
    validate_endpoint(doc.base_url, [doc.allowed_hostname])


def health(name: str) -> dict[str, str | int]:
    import frappe
    from frappe.utils import get_request_session

    doc = frappe.get_doc("AI Provider Configuration", name)
    doc.check_permission("read")
    if doc.status != "Enabled":
        return {"status": "disabled", "provider": doc.provider_name}
    from noxus_core.services.integrations import validate_endpoint

    validate_endpoint(doc.base_url, [doc.allowed_hostname])
    response = get_request_session().get(
        doc.base_url,
        headers={"Authorization": f"Bearer {doc.get_password('credential')}"},
        timeout=int(doc.timeout_seconds),
        allow_redirects=False,
    )
    response.raise_for_status()
    return {
        "status": "healthy",
        "provider": doc.provider_name,
        "http_status": response.status_code,
    }
