# NOXUS CORE 1.0.0rc1

This published release candidate contains the cross-platform CLI, strict module/blueprint/release schemas,
selective Django generator, checksummed Frappe runtime payload, nine Frappe apps, pinned Compose
topology, and compiled bilingual Solution Builder. It is available from
[PyPI](https://pypi.org/project/noxusai/1.0.0rc1/) and the immutable
[GitHub prerelease](https://github.com/5bv57zcm44-max/noxus-core/releases/tag/v1.0.0rc1).

Release qualification on 2026-07-28 passed the complete non-container Windows gate, Linux and
Windows CI on Python 3.11 and 3.14, frontend accessibility flows, repository security scans, and the
GitHub-hosted Website/PostgreSQL, Frappe-only, and ERPNext container suites. The container suites
create two real sites, run the Core tests, verify isolation, and exercise backup, gzip restore,
migration, restart, health, full SARIF reporting, and the fixable HIGH/CRITICAL image gate. Local
Docker was not used.

Publication was performed by the protected release workflow after it rebuilt and rechecked the wheel
and source distribution, reran all disposable container acceptance, wrote the SPDX JSON SBOM, and
generated GitHub build provenance. PyPI received both files through Trusted Publishing with
attestations. The wheel SHA-256 is
`2814839560c8b1f0aa3c56df1b4f922cfbe061667bfaa117868fdf8be71785b8`; the source distribution
SHA-256 is `ec16dde7d5135b6e7679bbd8bfe0fca48420875243a26da390aba98cf5ddcc46`.

React Router is upgraded to the patched 8.3.0 release and the frontend dependency audit has no
fixable HIGH/CRITICAL findings. The time-bounded upstream PDF disposition is documented separately.
Remote marketplace and cloud provisioning are intentionally unavailable.
