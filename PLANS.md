# NOXUS CORE implementation ledger

Status values: `pending`, `in progress`, `complete`, `blocked`.

| Phase | Status | Acceptance evidence |
| --- | --- | --- |
| 0. Discovery and foundations | complete | Local Git initialized; governance, architecture, product, threat-model, license, locks, immutable GitHub Action pins, and release policy are present. Repository policy checks are part of the 48-test Python gate and now require the manifest inventory to exactly match the payload. |
| 1. CLI foundation | complete | `python infrastructure/scripts/verify_release.py` passes Ruff, formatting, strict mypy, 48 Python tests, exact dependency audits, clean wheel installation, `--version`, JSON `doctor`, website/SaaS creation, and `pip check` on Windows. Doctor command timeouts are stable required failures or optional warnings. Click 8.3.3 is locked to remediate `PYSEC-2026-2132`; installation beside Bench is explicitly isolated. |
| 2. Website generator | in progress | Source and clean-wheel generated SQLite projects migrate and their seven emitted tests pass. Development and production Compose profiles and a PostgreSQL acceptance script are present. The generated Docker project completed migrations, health/OpenAPI probes, 21 PostgreSQL tests, backup, restore, restart, and cleanup in [Linux container run 30317845684](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30317845684). Representative minimal/full PostgreSQL generation coverage remains outstanding. |
| 3. Frappe environments | complete | Development/production Compose configurations validate; all images and upstream source commits are pinned. Both Frappe-only and ERPNext profiles in [container run 30326029016](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30326029016) built pinned sources, installed all nine apps and 53 DocTypes, started healthy services, passed the public API, verified apps, ran the Core Frappe tests, completed two-real-site isolation, backed up and restored the gzip database, migrated, restarted, returned healthy, and removed their volumes. The entrypoint keeps protected input handling privileged but performs all Frappe state changes as `frappe`. |
| 4. SDK and NOXUS Core | in progress | Strict contracts, resolver tests, 22 control DocTypes, services, APIs, migrations, permission tests, and opt-in two-real-site isolation coverage are present. The live Core Frappe test runner and two-real-site isolation gate pass in both Frappe-only and ERPNext profiles; broader permission, workflow, and recovery acceptance remains outstanding. |
| 5. React Solution Builder | in progress | ESLint, TypeScript strict mode, 2 Vitest tests, production Vite build, and two Playwright desktop/tablet flows pass in English and Arabic/RTL. axe-core reports zero WCAG A/AA violations on both flows. Live Frappe API contract coverage remains outstanding. |
| 6. Functional modules | in progress | Nine app manifests validate and their record/workflow/API contracts pass repository tests. Their 53 custom DocTypes now have a dependency-aware Link creation-order gate. Independent live installs and unauthorized workflow tests remain outstanding. |
| 7. Hardening and documentation | in progress | On 2026-07-28, local qualification passed Ruff, formatting, strict mypy, 48 Python tests, ESLint, TypeScript, Vitest, Playwright/WCAG, pip-audit, and npm audit with no known vulnerabilities. [CI run 30328481654](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30328481654) passed on Linux/Windows with Python 3.11/3.14 and the full frontend gate; [security run 30328492595](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30328492595) passed Gitleaks, pip-audit, npm audit, complete repository SARIF, the HIGH/CRITICAL gate, and upload. The replacement runtime keeps digest-pinned Bookworm for Frappe's required `wkhtmltopdf`, uses exact audited Socket.IO-only dependencies, applies patched Python overrides, and [container run 30328481668](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30328481668) passed Website/PostgreSQL, Frappe-only, ERPNext, complete image SARIF, and both fixable HIGH/CRITICAL gates. Release SBOM and provenance remain outstanding. |
| 8. Release candidate | in progress | On 2026-07-28, [release run 30329264846](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30329264846) passed the repeated content-addressed UI build, 48 Python tests, frontend/a11y/audit gates, sdist/wheel/Twine, complete SHA-256 verification, clean-wheel CLI/doctor, generated Django migrations/tests, packaged SaaS extraction, `pip check`, and all three disposable container suites. It then exposed a missing parent directory in the SBOM action; the workflow now creates that directory and uses the Node.js 24 SBOM action. A successful replacement SBOM/provenance run, immutable GitHub release, and PyPI publication remain outstanding. |

## Execution policy

At the end of every phase, run its tests, lint/type checks, inspect `git diff --check` and
`git status --short`, fix regressions, and replace the evidence cell above with exact commands and
results. Do not mark a phase complete based on scaffolding alone.

## Deferred external gates

- Local container execution is explicitly deferred because the workstation Docker installation is
  unavailable. No Docker daemon, Compose stack, image build, container, volume, or database was
  started during the 2026-07-28 qualification run.
- GitHub-hosted CI is externally blocked at account level. Runs
  [30310988149](https://github.com/AmrShalaby12/noxus-core/actions/runs/30310988149),
  [30310988243](https://github.com/AmrShalaby12/noxus-core/actions/runs/30310988243), and
  [30310988291](https://github.com/AmrShalaby12/noxus-core/actions/runs/30310988291) received no
  runner and executed no step; GitHub annotated every job with `The job was not started because your
  account is locked due to a billing issue.` Repository Actions are enabled and allow all actions.
- These are skipped for continued implementation only. They remain publication blockers and must be
  rerun on standard Linux runners after GitHub removes the account lock or on another authorized
  clean runner with Docker.
- The authorized fallback repository under `5bv57zcm44-max` supplies standard GitHub-hosted runners.
  Clean CI, the security workflow, and generated Website/PostgreSQL acceptance are green. The live
  runs exposed and validated corrections for clean-environment dependencies, PostgreSQL 18 storage,
  secret ownership, backup collisions, Frappe runtime prerequisites, local-app registration, and
  ERPNext frontend dependencies. Corrected Frappe/ERPNext and release-artifact runs must be green
  before publication.
