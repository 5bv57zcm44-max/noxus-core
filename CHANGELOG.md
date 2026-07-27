# Changelog

All notable changes follow Keep a Changelog and Semantic Versioning.

## [Unreleased]

### Added

- Initial production implementation for the `1.0.0rc1` release candidate.
- Separate non-container and full release-check targets for environments where Docker is unavailable.

### Fixed

- Rebuild and revalidate the complete release payload manifest after Vite emits content-addressed
  assets, preventing stale UI filenames from entering the wheel.
