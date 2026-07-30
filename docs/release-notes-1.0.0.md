# NOXUS CORE 1.0.0

NOXUS CORE 1.0.0 is the first stable community release. A single Python package installs the
cross-platform CLI and carries an immutable, checksummed payload for two independent creation paths:
a standalone Django/DRF website backend, or a self-hosted modular Frappe business system with an
optional unmodified ERPNext installation.

The stable release includes the strict module SDK and dependency resolver, custom email users and
production PostgreSQL settings for generated websites, nine bundled Frappe apps, one-site-per-tenant
isolation, guarded backup and restore, protected blueprint application, a bilingual LTR/RTL React
Solution Builder, and exact development and production Compose definitions. Standard wheel users do
not need Node.js because the compiled UI is included.

Release qualification runs on GitHub-hosted Linux and Windows environments. It covers supported CLI
Python versions, linting, typing, unit and accessibility tests, minimal and full generated PostgreSQL
projects, Frappe-only and ERPNext container profiles, independent app installation, live API and
permission boundaries, two-site isolation, backup/restore/restart, dependency and secret scanning,
an SPDX SBOM, and GitHub build provenance. Local Docker is not used for release qualification.

Install from PyPI with `pip install noxusai` or pin this immutable release with
`pip install noxusai==1.0.0`. The public release remains self-hosted: remote marketplace publishing,
cloud provisioning, and enabled AI providers are intentionally outside Community v1.
