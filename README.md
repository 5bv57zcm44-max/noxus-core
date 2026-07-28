# NOXUS CORE

NOXUS CORE generates secure standalone Django website backends and assembles modular, self-hosted
Frappe business systems. ERPNext is optional and remains unmodified.

```bash
pip install noxusai
noxusai doctor
noxusai new
```

Install the CLI in a dedicated virtual environment or with `pipx`; do not install it into the same
Python environment as Frappe Bench. Bench 5.31.0 constrains a vulnerable Click 8.2 line, while NOXUS
locks the remediated Click 8.3.3 release. The generated Frappe runtime remains isolated in containers.

The `1.0.0rc1` release candidate is published on
[PyPI](https://pypi.org/project/noxusai/1.0.0rc1/) and is installable with the command above. Pin the
exact candidate version for evaluated deployments: `pip install noxusai==1.0.0rc1`.

## Who it is for

- Developers who need a professional content and contact API for a company website.
- Teams building modular CRM, inventory, projects, support, maintenance, transport, or education
  systems on Frappe.
- Community module authors who need a validated manifest, dependency resolver, permissions,
  workflows, reports, and repeatable Docker environment.

## Architecture

The Python distribution contains the Typer/Rich CLI, strict Pydantic schemas, safe Jinja templates,
NOXUS Frappe app sources, compiled React UI, and checksummed deployment resources. Generated website
projects are independent Django/DRF applications. SaaS projects run one isolated Frappe site and
database per tenant. See [the architecture and threat model](docs/architecture.md).

## Prerequisites

- Python 3.11–3.14 for the CLI; Frappe container images use Python 3.14.
- Git for source development and `--edge` only.
- Docker Engine and Docker Compose for SaaS and Docker website workflows.
- Node.js 24.18.0 for monorepo UI development; normal wheel users receive compiled assets.

Run `noxusai doctor --workflow website` or `noxusai doctor --workflow saas` for real checks.

## Local development

Linux and macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
noxusai --version
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
noxusai --version
```

Install frontend dependencies with `npm install`. Run `make check test` on Unix or the equivalent
commands from the Makefile in PowerShell.

## Website generator

```bash
noxusai new website \
  --name acme-website \
  --database postgres \
  --auth both \
  --modules company,website,services,portfolio,team,contact,seo,media \
  --docker --yes
```

The generated README contains exact Docker and virtual-environment commands, migrations, seed data,
superuser creation, tests, health endpoints, and OpenAPI URLs.

## SaaS generator

```bash
noxusai new saas \
  --name acme-operations \
  --industry maintenance \
  --modules crm,inventory,maintenance \
  --with-erpnext --docker --yes
```

Stable creation extracts the versioned runtime bundled in the wheel. Development from an external
branch is explicit: `--edge --repository-url <url>`. The Community Deploy experience applies a
blueprint to the current site or produces local Docker/self-hosting instructions; it does not pretend
to provision cloud resources.

## Module development

```bash
noxusai module create repairs
noxusai module validate noxus_repairs
noxusai module list
```

Module manifests are schema-versioned and dependency installation is deterministic. ERPNext features
are adapters over an optional ERPNext installation, never core patches.

## Testing and deployment

- `make check` runs Python and frontend lint/type checks.
- `make test` runs fast Python and frontend tests.
- `make test-integration` runs service-dependent tests.
- `make test-e2e` runs Playwright.
- `make release-check-local` rebuilds the UI and release manifest, then validates every non-container
  release gate.
- `make release-check` additionally runs the destructive disposable container acceptance suites and
  remains mandatory before publication.

Deployment, backup, recovery, security, workflows, permissions, and troubleshooting documentation
lives under `docs/`. Release publication remains behind an explicit protected approval; `1.0.0rc1`
was published through PyPI Trusted Publishing after its complete GitHub-hosted release gate passed.
Maintainers should follow the [release and PyPI runbook](docs/releasing.md).

## Security, licensing, and contributing

Read [SECURITY.md](SECURITY.md) before reporting vulnerabilities and [CONTRIBUTING.md](CONTRIBUTING.md)
before submitting changes. Original NOXUS code and generated templates use GPL-3.0-or-later. Dependency
licenses remain their own; [licensing guidance](docs/licensing.md) is not legal advice.

The immediate roadmap is tracked with evidence in [PLANS.md](PLANS.md) and changes in
[CHANGELOG.md](CHANGELOG.md).
