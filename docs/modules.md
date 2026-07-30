# Module SDK and authoring

Every module carries strict `noxus-module.yml` schema version 1. Unknown fields fail validation.
Dependencies use concise PEP 440 syntax such as `noxus_core>=1.0.0`; required, recommended, and
conflicting edges are distinct. The resolver validates Python/Frappe/ERPNext constraints, detects
missing nodes and explicit cycles, and emits a deterministic topological order.

```powershell
noxusai module create repairs --directory .\frappe_apps
noxusai module validate .\frappe_apps\noxus_repairs
noxusai module install repairs --yes
```

Generated apps contain a working manifest, hook, service, API, permission fixture, workflow fixture,
report, patch, and test. Module RPC methods live below `/api/v2/method/noxus_<name>.api.v1.*`.
Accounting, Sales, Purchasing, and Manufacturing are adapters activated only when the one optional
ERPNext app is installed; they are never forks.
