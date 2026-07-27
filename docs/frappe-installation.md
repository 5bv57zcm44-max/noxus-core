# Frappe installation

NOXUS builds Frappe commit `be4728af84ecdec9e3e555f0aca1a7766d3f1811` (tag `v16.28.0`) into a
local image with Python 3.14.6. Optional ERPNext uses commit
`a5de60c357d531cb31da093f0b86301776965173` (tag `v16.29.0`). Stable CLI installs extract checksummed
wheel resources and never clone NOXUS. `--edge` requires an explicit URL and branch.

```bash
noxusai new saas --name operations --modules crm,inventory,support --yes
printf '%s' 'a-long-random-password' > operations/secrets/admin_password.txt
chmod 600 operations/secrets/admin_password.txt
cd operations
docker compose --profile development up --build --detach
```

On Windows use Docker Desktop Linux containers and preferably WSL2. Bare-metal Frappe production is
supported only on Linux. Existing benches use `noxusai init --bench <path> --site <site>`.
