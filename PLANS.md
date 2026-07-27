# NOXUS CORE implementation ledger

Status values: `pending`, `in progress`, `complete`, `blocked`.

| Phase | Status | Acceptance evidence |
| --- | --- | --- |
| 0. Discovery and foundations | complete | Local Git initialized; governance, architecture, product, threat-model, license, locks, immutable GitHub Action pins, and release policy are present. Repository policy checks are part of the 26-test Python gate. |
| 1. CLI foundation | complete | `python infrastructure/scripts/verify_release.py` passes Ruff, formatting, strict mypy, 26 Python tests, exact dependency audits, clean wheel installation, `--version`, JSON `doctor`, website/SaaS creation, and `pip check` on Windows. Click 8.3.3 is locked to remediate `PYSEC-2026-2132`; installation beside Bench is explicitly isolated. |
| 2. Website generator | in progress | Source and clean-wheel generated SQLite projects migrate and their seven emitted tests pass. Development and production Compose profiles and a PostgreSQL acceptance script are present; live PostgreSQL container acceptance remains outstanding. |
| 3. Frappe environments | in progress | Development/production Compose configurations validate; all images and upstream source commits are pinned. Live Frappe-only and ERPNext image, restart, backup, and restore gates remain outstanding. |
| 4. SDK and NOXUS Core | in progress | Strict contracts, resolver tests, 22 control DocTypes, services, APIs, migrations, permission tests, and opt-in two-real-site isolation coverage are present. A live Frappe test-runner execution remains outstanding. |
| 5. React Solution Builder | in progress | ESLint, TypeScript strict mode, 2 Vitest tests, production Vite build, and two Playwright desktop/tablet flows pass in English and Arabic/RTL. axe-core reports zero WCAG A/AA violations on both flows. Live Frappe API contract coverage remains outstanding. |
| 6. Functional modules | in progress | Nine app manifests validate and their record/workflow/API contracts pass repository tests. Independent live installs and unauthorized workflow tests remain outstanding. |
| 7. Hardening and documentation | in progress | CI/release/scanning workflows, operational documentation, tutorials, full GPL text, zero known pip/npm vulnerabilities, Twine metadata validation, and no accepted audit exceptions are present. CI-hosted Trivy, Gitleaks, SBOM, and provenance gates remain outstanding. |
| 8. Release candidate | in progress | The non-container release checker passes deterministic UI build, Playwright/WCAG, sdist, wheel, Twine, SHA-256 payload verification, clean-wheel website migration/tests, and packaged SaaS extraction. Per user instruction, local Docker was not run; Linux container acceptance, artifact attestation, GitHub upload, and PyPI publication remain outstanding. |

## Execution policy

At the end of every phase, run its tests, lint/type checks, inspect `git diff --check` and
`git status --short`, fix regressions, and replace the evidence cell above with exact commands and
results. Do not mark a phase complete based on scaffolding alone.
