# Security scanner dispositions

Fixable HIGH and CRITICAL findings are publication blockers. Container scans use Trivy's
`ignore-unfixed` policy so a release is not indefinitely blocked by a distribution or upstream
package that publishes no patched version. Those findings remain visible in the release SBOM and
are reevaluated by the scheduled weekly scan; this policy never suppresses a finding with an
available fix.

Trivy's SARIF format intentionally reports every severity by default. CI therefore performs one
nonblocking all-severity SARIF scan for the GitHub Security view and a separate table-format scan
whose exit code blocks fixable HIGH/CRITICAL findings. The blocking decision never depends on
SARIF's reporting behavior.

The Frappe runtime remains on its digest-pinned Debian Bookworm base because
[Debian Trixie does not publish `wkhtmltopdf`](https://packages.debian.org/search?keywords=wkhtmltopdf),
which Frappe's supported PDF path requires. Distribution findings without vendor fixes follow the
time-bounded policy above; replacing the PDF runtime with an unverified cross-distribution binary
is not an acceptable security tradeoff.

The pinned Frappe 16.28.0 metadata constrains Pillow, pypdf, and cryptography to versions for which
fixes became available after that Frappe release. The image applies exact overrides to Pillow
12.3.0, pypdf 6.14.2, and cryptography 48.0.1. Both Frappe-only and ERPNext installations, Frappe's
Core tests, backup/restore/migrate/restart, health checks, and two-site isolation must pass with
those overrides before release.

`CVE-2025-26240` has no fixed python-pdfkit release. At the pinned Frappe commit,
[`get_pdf`](https://github.com/frappe/frappe/blob/be4728af84ecdec9e3e555f0aca1a7766d3f1811/frappe/utils/pdf.py#L103)
disables JavaScript and local-file access before calling `pdfkit.from_string`, and
[`FrappePDFKit`](https://github.com/frappe/frappe/blob/be4728af84ecdec9e3e555f0aca1a7766d3f1811/frappe/utils/pdf.py#L39)
overrides pdfkit's HTML meta-option parser so untrusted markup cannot re-enable either capability.
This disposition expires on 2026-08-28 or immediately when the Frappe PDF implementation, pdfkit
dependency, or wkhtmltopdf invocation changes. Any such change blocks publication until the review
is repeated.

React Router was moved from 7.18.1 to the patched 8.3.0 package on 2026-07-27 in response to
`GHSA-qwww-vcr4-c8h2`; no exception is retained for the previous version.
