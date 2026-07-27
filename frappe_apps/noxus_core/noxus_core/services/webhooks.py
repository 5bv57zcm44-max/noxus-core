from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def sign(secret: str, body: bytes, timestamp: str) -> str:
    return hmac.new(secret.encode(), timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()


def verify(secret: str, body: bytes, timestamp: str, signature: str) -> bool:
    return hmac.compare_digest(sign(secret, body, timestamp), signature)


def deliver(endpoint_name: str, payload: dict[str, Any]) -> None:
    import frappe
    from frappe.utils import get_request_session, now_datetime

    from noxus_core.services.integrations import validate_endpoint

    endpoint = frappe.get_doc("Webhook Endpoint", endpoint_name)
    if not endpoint.enabled:
        return
    definition = (
        frappe.db.get_value("Integration Definition", {"provider": "webhook"}, "endpoint_allowlist")
        or ""
    )
    allowlist = [item.strip() for item in definition.splitlines() if item.strip()]
    validate_endpoint(endpoint.url, allowlist)
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    timestamp = now_datetime().isoformat()
    signature = sign(endpoint.get_password("signing_secret"), body, timestamp)
    response = get_request_session().post(
        endpoint.url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Noxus-Timestamp": timestamp,
            "X-Noxus-Signature": signature,
        },
        timeout=10,
        allow_redirects=False,
    )
    response.raise_for_status()
