# NOXUS CORE implementation ledger

Status values: `pending`, `in progress`, `complete`, `blocked`.

| Phase | Status | Acceptance evidence |
| --- | --- | --- |
| 0. Discovery and foundations | complete | Local Git initialized; governance, architecture, product, threat-model, license, locks, immutable GitHub Action pins, and release policy are present. Repository policy checks are part of the 54-test Python gate and require the manifest inventory to exactly match the payload. |
| 1. CLI foundation | complete | `python infrastructure/scripts/verify_release.py` passes Ruff, formatting, strict mypy, 54 Python tests, exact dependency audits, clean wheel installation, `--version`, JSON `doctor`, website/SaaS creation, and `pip check` on Windows. Doctor command timeouts are stable required failures or optional warnings. Click 8.3.3 is locked to remediate `PYSEC-2026-2132`; installation beside Bench is explicitly isolated. |
| 2. Website generator | complete | Source and clean-wheel generated SQLite projects migrate and their seven emitted tests pass. In [stable container run 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854), independent minimal/session/English and full/both/bilingual PostgreSQL projects completed migrations, health/OpenAPI probes, 21 tests, backup, restore, restart, and cleanup. |
| 3. Frappe environments | complete | Development/production Compose configurations validate; all images and upstream source commits are pinned. Both profiles in [stable container run 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854) built pinned Frappe/ERPNext sources, installed all nine apps and 53 DocTypes, started healthy services, completed recovery and restart, removed their volumes, and passed fixable high/critical Trivy gates. Build-only pip, npm, Yarn, and caches are absent from the flattened runtime image. |
| 4. SDK and NOXUS Core | complete | Strict contracts, resolver tests, 22 control DocTypes, services, APIs, migrations, permission tests, and two-real-site isolation coverage pass. [Stable container run 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854) also passed guest catalog denial, invalid blueprint checksum, unknown workflow and arbitrary automation rejection, authorized/unauthorized workflow transitions, backup/restore, and restart recovery. |
| 5. React Solution Builder | complete | ESLint, TypeScript strict mode, 2 Vitest tests, production Vite build, and two Playwright desktop/tablet flows pass in English and Arabic/RTL; axe-core reports zero WCAG A/AA violations. The live proxy login, catalog, marketplace-unavailable, and resolver contracts passed in [stable container run 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854). |
| 6. Functional modules | complete | Nine app manifests validate and their record/workflow/API contracts pass repository tests. Their 53 custom DocTypes pass dependency-aware Link creation order. [Stable container run 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854) created an independent live site for every app, installed Inventory before Maintenance, and rejected unauthorized Support transitions. |
| 7. Hardening and documentation | in progress | On 2026-07-30, local non-container qualification passed Ruff, formatting, strict mypy, 54 Python tests, ESLint, TypeScript, 2 Vitest tests, 2 Playwright desktop/tablet English/Arabic/RTL flows, exact Python/npm audits with no known vulnerabilities, stable sdist/wheel/Twine checks, and a clean-wheel smoke test that returned `1.0.0`, migrated and ran 7 generated Django tests, extracted the checksummed SaaS payload, and passed `pip check`. Local Docker remained unused. Stable commit `c2911b1` passed [CI 30509232890](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232890), [security 30509232878](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232878), and [container acceptance 30509232854](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30509232854). The full SBOM/provenance release workflow remains outstanding. |
| 8. Release candidate | complete | On 2026-07-28, [release run 30345016500](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30345016500) passed the content-addressed UI build, 48 Python tests, frontend/a11y/audit gates, sdist/wheel/Twine checks, complete SHA-256 verification, clean-wheel CLI/doctor, generated Django migrations/tests, packaged SaaS extraction, `pip check`, all three disposable container suites, SPDX SBOM generation, and provenance. The immutable [GitHub prerelease](https://github.com/5bv57zcm44-max/noxus-core/releases/tag/v1.0.0rc1) and [PyPI `1.0.0rc1` release](https://pypi.org/project/noxusai/1.0.0rc1/) are public. Both `pip install noxusai==1.0.0rc1` and unversioned `pip install noxusai` were verified without cache in new Windows/Python 3.14 virtual environments; `--version` returned `1.0.0rc1` and JSON website doctor returned `ok: true`. |
| 9. Stable release | in progress | Version, package metadata, Frappe apps, manifests, UI, generated-project locks, Compose image names, examples, release notes, and checksummed payload are synchronized at `1.0.0`. Stable publication is blocked until the new GitHub-hosted CI, security, container, SBOM, and provenance gates pass. |

## Execution policy

At the end of every phase, run its tests, lint/type checks, inspect `git diff --check` and
`git status --short`, fix regressions, and replace the evidence cell above with exact commands and
results. Do not mark a phase complete based on scaffolding alone.

## External qualification outcome

- Local container execution remains intentionally unused because the workstation Docker installation
  is unavailable. No local daemon, Compose stack, image, container, volume, or database was started.
- The authorized public repository under `5bv57zcm44-max` supplied clean standard GitHub-hosted
  Linux/Windows runners. Stable CI, security, Website/PostgreSQL, Frappe-only, and ERPNext gates are
  green. Stable SBOM, provenance, publication, and post-publication checks remain pending.
- The earlier runner/billing block on the other GitHub account is historical and is no longer a
  release blocker. Publication came only from the qualified `main` workflow through short-lived OIDC.
