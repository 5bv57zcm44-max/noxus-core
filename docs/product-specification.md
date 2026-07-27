# Product specification

NOXUS CORE is an open-source developer platform for generating standalone company website backends
and assembling self-hosted modular business systems. Its distribution and command are both
`noxusai`.

## Personas and outcomes

- Website developers select only the content and communication modules they need and receive a
  documented Django/DRF project that works with or without Docker.
- Business-system developers select an industry, modules, features, roles, workflows, integrations,
  and branding, then receive a reproducible Frappe site and Solution Blueprint.
- Module authors create, validate, test, install, and publish GPL-compatible Frappe apps through a
  versioned manifest contract.

## Community release boundary

Community v1 creates local and self-hosted configurations. It can apply a blueprint to a current
site, but it does not provision a cloud account or claim that infrastructure exists. ERPNext is an
optional application and remains unmodified.

## Acceptance

The authoritative release gate is `infrastructure/scripts/verify_release.py` plus the CLI, generated
Django, Frappe, UI, security, Docker, and clean-wheel test suites described in `PLANS.md`.
