# Security policy

The project is pre-release; only the current release-candidate line receives security fixes.

Do not open a public issue for a suspected vulnerability. Contact the maintainers privately with the
affected version, reproduction, impact, and suggested mitigation. Do not include real credentials or
customer data. We will acknowledge a report, assess severity, coordinate a fix, and publish an
advisory after users have a reasonable update path.

Secrets must live in environment files excluded from Git, Docker secrets, or the Frappe encrypted
password store. See `docs/architecture.md` for trust boundaries and threat mitigations.
