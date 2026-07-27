# CLI reference

Install NOXUS in an isolated environment. Either `pipx install noxusai`, or create and activate a
dedicated Python virtual environment before running `python -m pip install noxusai`. Do not install
the CLI into a Frappe Bench environment: Bench 5.31.0 constrains Click to `~=8.2.0`, while NOXUS
requires the security-fixed Click 8.3.3 for `PYSEC-2026-2132`.

Global options precede the command: `--dry-run`, `--verbose`, `--json`, and `--no-color`. JSON mode
always emits `{ok, command, data, warnings, error}`. Exit codes are 0 success, 2 usage, 3 missing
prerequisite, 4 conflict, 5 cancellation, 6 partial failure, 7 permission, 8 unsafe action, 9 failed
health gate, and 10 network failure.

Run `noxusai doctor --workflow website|saas|edge`. Project commands discover `.noxus/project.yml`
from the current directory upward. Precedence is command flag, `NOXUS_*` environment, project YAML,
user config, then safe default. Commands are documented with `noxusai COMMAND --help`.

Destructive module uninstall and restore display the resolved site, project, and archive. Automation
requires both `--yes` and the exact `--confirm-target` value printed by the dry run.

PowerShell example:

```powershell
noxusai --json --dry-run new saas --name operations --modules crm,inventory --yes
noxusai restore --archive D:\backups\site.sql.gz --target operations.localhost `
  --yes --confirm-target operations.localhost
```
