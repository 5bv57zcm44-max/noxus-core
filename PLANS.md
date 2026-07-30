# NOXUS CORE implementation ledger

Status values: `pending`, `in progress`, `complete`, `blocked`.

| Phase | Status | Acceptance evidence |
| --- | --- | --- |
| 0. Discovery and foundations | complete | Local Git initialized; governance, architecture, product, threat-model, license, locks, immutable GitHub Action pins, and release policy are present. Repository policy checks are part of the 48-test Python gate and now require the manifest inventory to exactly match the payload. |
| 1. CLI foundation | complete | `python infrastructure/scripts/verify_release.py` passes Ruff, formatting, strict mypy, 48 Python tests, exact dependency audits, clean wheel installation, `--version`, JSON `doctor`, website/SaaS creation, and `pip check` on Windows. Doctor command timeouts are stable required failures or optional warnings. Click 8.3.3 is locked to remediate `PYSEC-2026-2132`; installation beside Bench is explicitly isolated. |
| 2. Website generator | in progress | Source and clean-wheel generated SQLite projects migrate and their seven emitted tests pass. Development and production Compose profiles and a PostgreSQL acceptance script are present. The generated Docker project completed migrations, health/OpenAPI probes, 21 PostgreSQL tests, backup, restore, restart, and cleanup in [Linux container run 30317845684](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30317845684). The stable gate now generates independent minimal/session/English and full/both/bilingual PostgreSQL projects; qualifying that expanded gate on GitHub remains outstanding. |
| 3. Frappe environments | complete | Development/production Compose configurations validate; all images and upstream source commits are pinned. Both Frappe-only and ERPNext profiles in [container run 30326029016](https://github.com/5bv57zcm44-max/noxus-core/actions/runs/30326029016) built pinned sources, installed all nine apps and 53 DocTypes, started healthy services, passed the public API, verified apps, ran the Core Frappe tests, completed two-real-site isolation, backed up and restored the gzip database, migrated, restarted, returned healthy, and removed their volumes. The entrypoint keeps protected input handling privileged but performs all Frappe state changes as `frappe`. |
| 4. SDK and NOXUS Core | in progress | Strict contracts, resolver tests, 22 control DocTypes, services, APIs, migrations, permission tests, and opt-in two-real-site isolation coverage are present. The stable Frappe suite adds guest catalog denial, invalid blueprint checksum, unknown workflow and arbitrary automation rejection, authorized/unauthorized workflow transitions, and existing recovery coverage; its GitHub container qualification remains outstanding. |
| 5. React Solution Builder | in progress | ESLint, TypeScript strict mode, 2 Vitest tests, production Vite build, and two Playwright desktop/tablet flows pass in English and Arabic/RTL. axe-core reports zero WCAG A/AA violations on both flows. The stable container gate now exercises login plus real catalog and resolver responses through the public proxy; its GitHub qualification remains outstanding. |
| 6. Functional modules | in progress | Nine app manifests validate and their record/workflow/API contracts pass repository tests. Their 53 custom DocTypes have a dependency-aware Link creation-order gate. The stable container suite now creates an independent live site for every app (and Inventory before Maintenance) and rejects unauthorized Support transitions; its GitHub qualification remains outstanding. |
| 7. Hardening and documentation | in progress | On 2026-07-30, local non-container qualification passed Ruff, formatting, strict mypy, 54 Python tests, ESLint, TypeScript, 2 Vitest tests, 2 Playwright desktop/tablet English/Arabic/RTL flows, exact Python/npm audits with no known vulnerabilities, stable sdist/wheel/Twine checks, and a clean-wheel smoke test that returned `1.0.0`, migrated and ran 7 generated Django tests, extracted the checksummed SaaS payload, and passed `pip check`. Local Docker remained unused. GitHub CI, security, container, SBOM, and provenance qualification for the stable commit remains outstanding. |
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
  Linux/Windows runners. CI, security, Website/PostgreSQL, Frappe-only, ERPNext, SBOM, provenance,
  package publication, and post-publication installation checks are green.
- The earlier runner/billing block on the other GitHub account is historical and is no longer a
  release blocker. Publication came only from the qualified `main` workflow through short-lived OIDC.
