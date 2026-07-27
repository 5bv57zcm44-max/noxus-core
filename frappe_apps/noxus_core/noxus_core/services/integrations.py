from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


def validate_endpoint(url: str, allowlist: list[str]) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Integration endpoints require an HTTPS hostname without URL credentials")
    if parsed.hostname not in allowlist:
        raise ValueError("Integration endpoint hostname is not allow-listed")
    for result in socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM):
        address = ipaddress.ip_address(result[4][0])
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
        ):
            raise ValueError("Integration endpoint resolves to a non-public address")


def validate_credential(doc, method: str | None = None) -> None:
    secret = doc.get_password("credential") if not doc.is_new() else doc.credential
    doc.last_four = secret[-4:] if secret else ""


def validate_webhook(doc, method: str | None = None) -> None:
    import frappe

    definition = (
        frappe.db.get_value("Integration Definition", {"provider": "webhook"}, "endpoint_allowlist")
        or ""
    )
    validate_endpoint(doc.url, [item.strip() for item in definition.splitlines() if item.strip()])
