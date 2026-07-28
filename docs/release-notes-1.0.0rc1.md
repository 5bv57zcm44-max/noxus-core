# NOXUS CORE 1.0.0rc1

This local release candidate contains the cross-platform CLI, strict module/blueprint/release schemas,
selective Django generator, checksummed Frappe runtime payload, nine Frappe apps, pinned Compose
topology, and compiled bilingual Solution Builder. It has not been published.

Release qualification on 2026-07-28 passed the complete non-container Windows gate, Linux and
Windows CI on Python 3.11 and 3.14, frontend accessibility flows, repository security scans, and the
GitHub-hosted Website/PostgreSQL, Frappe-only, and ERPNext container suites. The container suites
create two real sites, run the Core tests, verify isolation, and exercise backup, gzip restore,
migration, restart, health, full SARIF reporting, and the fixable HIGH/CRITICAL image gate. Local
Docker was not used.

Publication remains protected by the release workflow. That workflow rebuilds and rechecks the
wheel and source distribution, reruns all disposable container acceptance, writes an SPDX JSON
SBOM, generates GitHub build provenance, and uploads immutable artifacts before either a tag release
or an explicitly authorized PyPI job can proceed.

React Router is upgraded to the patched 8.3.0 release and the frontend dependency audit has no
fixable HIGH/CRITICAL findings. The time-bounded upstream PDF disposition is documented separately.
Remote marketplace and cloud provisioning are intentionally unavailable.
