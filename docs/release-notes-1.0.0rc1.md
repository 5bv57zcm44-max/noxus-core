# NOXUS CORE 1.0.0rc1

This local release candidate contains the cross-platform CLI, strict module/blueprint/release schemas,
selective Django generator, checksummed Frappe runtime payload, nine Frappe apps, pinned Compose
topology, and compiled bilingual Solution Builder. It has not been published.

Release qualification on 2026-07-28 passed the complete non-container Windows gate, including the
clean-wheel Django migration/tests and checksummed SaaS payload extraction. Full Frappe/ERPNext
Docker acceptance, two-site isolation, SBOM/provenance, and Linux CI remain required before
publication. They are deferred because the local Docker installation is unavailable and GitHub
refused to allocate every hosted runner with an account-level billing lock before any workflow step.
This is recorded as an external blocker, not a passed gate.

React Router is upgraded to the patched 8.3.0 release and the frontend dependency audit has no
accepted security exceptions. Remote marketplace and cloud provisioning are intentionally
unavailable.
