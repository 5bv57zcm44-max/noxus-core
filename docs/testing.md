# Test strategy

`make check`, `make test`, `make test-integration`, `make test-e2e`, `make build`, and
`make release-check` are the standard gates. PowerShell equivalents are:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest -q
npm run lint
npm run typecheck
npm test
npm run build
python -m build
```

Service acceptance is opt-in: set `NOXUS_RUN_DOCKER_ACCEPTANCE=1` and run
`python -m pytest infrastructure/tests -m docker`. Also set `NOXUS_DOCKER_PROJECT` to a disposable,
generated SaaS project and provide `NOXUS_TEST_ADMIN_PASSWORD` through the protected environment.
The current suite builds pinned images, creates two real sites, installs NOXUS Core in each, and
proves that the same logical identifier resolves to site-specific data. Run the Frappe app tests for
permissions and workflows as a separate gate. Never use a production project or credentials.
