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
