# Changelog

All notable changes follow Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Added

- Initial production implementation for the `1.0.0rc1` release candidate.
- Separate non-container and full release-check targets for environments where Docker is unavailable.

### Fixed

- Rebuild and revalidate the complete release payload manifest after Vite emits content-addressed
  assets, preventing stale UI filenames from entering the wheel.
- Install the generated Django project's exact test dependencies in clean development environments.
- Mount PostgreSQL 18 data at its supported parent directory and preserve failure logs and cleanup.
- Install pinned Yarn in the Frappe image and correct the pinned Trivy security workflow inputs.
- Read protected Compose secret files before dropping the generated website container to `django`.
- Route generated website container test commands through the secret-loading entrypoint.
- Install bundled Frappe apps and pinned ERPNext source directly instead of parsing local paths as remotes.
- Install ERPNext's exact Yarn lock before building its pinned frontend assets.
- Give every backup a collision-resistant UTC/UUID directory before restore preflight.
- Capture Frappe service logs and remove volumes when Compose fails during partial startup.
- Load protected Frappe site secrets as root, then immediately drop to the `frappe` user.
- Run Frappe site creation from the Bench `sites` directory so app discovery and logging resolve correctly.
- Provide the standard nested Frappe module package declared by every NOXUS app.
- Declare complete Frappe release metadata for all apps and hide internal schema imports from hooks.
- Validate Dynamic Link contracts and point the optional ERPNext item adapter through `DocType`.
- Create the Maintenance Technician before Work Orders that link to it and validate every bundled
  custom DocType Link against dependency-aware Frappe installation order.
- Convert doctor command timeouts into required failures or optional warnings instead of crashing.
