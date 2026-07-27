# Repository instructions

## Product boundaries

- NOXUS CORE has two independent creation paths: a standalone generated Django backend and a
  Docker-based Frappe business system. Do not make generated Django projects depend on Frappe.
- ERPNext is optional. Never patch or fork ERPNext for a NOXUS feature.
- Community deployment is self-hosted. Do not represent configuration generation as cloud
  provisioning.

## Engineering rules

- Preserve the public contracts in `module_sdk/noxus_module_sdk` and version them deliberately.
- Never invoke subprocesses with `shell=True`; pass validated argument arrays.
- Never log secrets or accept administrator passwords as command-line values.
- Every protected operation needs server-side permission checks; UI visibility is not security.
- Use one Frappe site/database per tenant. Do not introduce shared-tenant rows without a new threat
  model and migration plan.
- Keep business logic in services, not Typer commands, Frappe DocType event handlers, or React
  components.

## Required checks

Run `make check` and `make test` for normal changes. Changes to templates, containers, migrations,
permissions, authentication, backup/restore, or release packaging also require their relevant
integration or release checks. Record completed phase evidence in `PLANS.md`.
