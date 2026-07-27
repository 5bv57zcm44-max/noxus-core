# Test strategy

`make check`, `make test`, `make test-integration`, `make test-e2e`, `make build`,
`make release-check-local`, and `make release-check` are the standard gates. The local release gate
does not invoke Docker; the full release gate does. PowerShell equivalents for preparing and running
the non-container release gate are:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest -q
npm run lint
npm run typecheck
npm test
npm run build
python infrastructure/scripts/build_release_manifest.py
python infrastructure/scripts/verify_release.py
```

The manifest must be generated only after the production UI build. The verifier builds the UI again
and rechecks the complete payload inventory and every SHA-256 digest before assembling the wheel.
This prevents renamed Vite assets or any unlisted payload file from entering an artifact.

Service acceptance is opt-in: set `NOXUS_RUN_DOCKER_ACCEPTANCE=1` and run
`python -m pytest infrastructure/tests -m docker`. Also set `NOXUS_DOCKER_PROJECT` to a disposable,
generated SaaS project and provide `NOXUS_TEST_ADMIN_PASSWORD` through the protected environment.
The current suite builds pinned images, creates two real sites, installs NOXUS Core in each, and
proves that the same logical identifier resolves to site-specific data. Run the Frappe app tests for
permissions and workflows as a separate gate. Never use a production project or credentials.

If container acceptance is temporarily unavailable, record the exact external blocker in
`PLANS.md`; do not mark the affected phase complete and do not publish the release candidate.
