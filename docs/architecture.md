# Architecture

## System boundaries

The `noxusai` wheel contains the CLI, strict schemas, website templates, NOXUS Frappe app sources,
compiled UI assets, and reproducible deployment definitions. A website project is rendered directly
from safe templates and has no runtime relationship with the monorepo. A SaaS project extracts a
checksummed runtime payload and builds Frappe containers locally.

Frappe is the control-plane backend. The React SPA is a separately built client served at `/noxus`;
the edge proxy keeps the SPA, Frappe API, files, assets, and websocket on one origin. Each tenant is a
Frappe site with its own database. ERPNext, when selected, is installed as an unmodified app.

## Data and control flow

1. The CLI validates explicit input and prerequisites, renders a review plan, journals intended
   operations, and invokes tools with argument arrays.
2. The module SDK validates manifests and blueprints before filesystem, Docker, or database changes.
3. Frappe services authorize and execute registry, blueprint, role, workflow, integration, and
   deployment changes; event handlers remain thin.
4. The React client fetches authenticated, versioned APIs. Backend permissions and tenant routing are
   authoritative.

## Threat model

| Threat | Boundary | Primary mitigations |
| --- | --- | --- |
| Path traversal/template injection | CLI to filesystem | Slug validation, resolved-path containment, Jinja strict mode, no evaluation |
| Command injection | CLI to OS/Docker/Git | Argument arrays, command allow-list, no `shell=True`, redacted journals |
| Secret disclosure | CLI/log/API/backup | Secret files or protected environment, structured redaction, one-time credential reveal, encrypted fields |
| IDOR/mass assignment | React/API/Frappe | Authenticated session, DocType and object checks, allow-listed mutable fields, negative tests |
| Cross-tenant access | Proxy/Frappe/sites | Host allow-list, site-per-database, no trusted public site header, two-site tests |
| CSRF/CORS abuse | Browser/API | Same-origin production, CSRF tokens, explicit development origins, secure cookies |
| Malicious uploads | Public and authenticated APIs | Size/type allow-list, randomized paths, image decoding, private-by-default storage |
| SSRF/webhook forgery | Integration services | HTTPS and host allow-lists, private-address rejection, timeouts, HMAC signatures, replay window |
| Workflow/automation abuse | Rules to documents | Declarative actions only, permission recheck, idempotency, audit records, no arbitrary Python |
| Supply-chain compromise | Build/release | Exact locks/tags/digests, hash manifest, SBOM, provenance, dependency/container/secret scans |
| Destructive recovery | Restore/update/uninstall | Exact target display, confirmation, preflight backup, staged image, operation journal |

## Upgrade strategy

Release manifests bind NOXUS, Frappe, ERPNext, database, cache, and UI versions. SaaS upgrades stage a
new image, take a backup, migrate, run health checks, and retain the previous image plus backup.
Generated websites update only files whose recorded hashes prove they are unedited; all other changes
become an explicit conflict plan.
