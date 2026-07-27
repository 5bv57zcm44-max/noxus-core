# Verified version matrix

Verified on 2026-07-27 and pinned for `1.0.0rc1`:

| Component | Pin | Policy |
| --- | --- | --- |
| Python container runtime | 3.14.6 | Frappe requires 3.14.x |
| CLI Python | >=3.11,<3.15 | CI tests each supported minor |
| Django | 5.2.16 | LTS |
| Django REST Framework | 3.17.1 | Latest compatible stable |
| Typer | 0.27.0 | Exact wheel dependency |
| Click | 8.3.3 | Fixes `PYSEC-2026-2132`; isolate from Frappe Bench |
| Frappe | 16.28.0 | Exact tag and commit recorded in release manifest |
| ERPNext | 16.29.0 | Optional exact tag and commit |
| Node.js | 24.18.0 | LTS build runtime |
| MariaDB | 11.8.6 | LTS database runtime |
| Redis | 7.2.14 | Mature supported security release |
| React / Vite / TypeScript | 19.2.8 / 8.1.5 / 7.0.2 | Exact npm lock |
| React Router | 8.3.0 | Fixes `GHSA-qwww-vcr4-c8h2` |
| TanStack Query / Tailwind | 5.101.4 / 4.3.3 | Exact npm lock |
| Vitest / Playwright | 4.1.10 / 1.62.0 | Exact npm lock |

Container image references add immutable per-architecture digests in the release manifest. A version
change requires compatibility tests and a changelog entry; production definitions never use
`latest` or an unpinned branch.
