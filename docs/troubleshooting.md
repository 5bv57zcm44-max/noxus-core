# Troubleshooting

- If pip reports a Click conflict with `frappe-bench`, remove NOXUS from that environment and install
  it with `pipx install noxusai` or in a dedicated virtual environment. Do not downgrade Click below
  8.3.3; older versions are affected by `PYSEC-2026-2132`.
- Run `noxusai --json doctor --workflow saas` and inspect required failures.
- Run `docker compose --profile development ps` and `noxusai logs` for container state.
- A blank administrator secret intentionally stops `site-creator`; populate the protected file and
  rerun the service.
- Hostname response 421 means the request host is not the configured `NOXUS_SITE` allow-list entry.
- Website production refuses SQLite and the development secret key by design.
- An update conflict is not a partial overwrite; review `.noxus/update-plan.yml`, merge manually,
  then retain the resulting file.
- For failed blueprints, inspect Deployment Record and Audit Event, resolve the reported stage, and
  resume using the same idempotency key.
