# Release and PyPI runbook

Only maintainers may publish NOXUS CORE. A release is built on GitHub-hosted Linux runners; never
upload a workstation build, bypass a failed gate, reuse a version, or paste a PyPI password or API
token into a command, issue, log, or repository secret.

## One-time PyPI trusted publisher setup (completed for `noxusai`)

PyPI does not charge for publishing a public package. The first `noxusai` release used a
**Pending Trusted Publisher** with these exact values:

| Field | Value |
| --- | --- |
| PyPI project | `noxusai` |
| GitHub owner | `5bv57zcm44-max` |
| Repository | `noxus-core` |
| Workflow | `release.yml` |
| Environment | `pypi-production` |

The GitHub environment permits deployment only from `main`. PyPI converted the pending publisher to
a normal project publisher when `1.0.0rc1` was uploaded successfully on 2026-07-28. Future releases
must preserve the same repository/workflow/environment identity and use the protected workflow;
never create or store a long-lived PyPI token as a workaround.

## Release procedure

1. Confirm `main` is clean and all CI, Security, and Container acceptance checks are green.
2. Dispatch **Prepare release** with `authorize_pypi=false`. Verify the Python distributions,
   `noxus-core.spdx.json`, and GitHub provenance artifacts.
3. Confirm the version in `pyproject.toml`, release notes, changelog, and tag are identical. Tags are
   immutable; for this candidate the tag is `v1.0.0rc1`.
4. Create and push the signed or annotated tag. The tag workflow reruns the full release gate and
   creates the GitHub release only after the artifacts job succeeds.
5. Dispatch **Prepare release** from `main` with `authorize_pypi=true`. The protected
   `pypi-production` job downloads the already qualified artifacts and publishes through short-lived
   OIDC credentials.
6. Verify the PyPI JSON endpoint, install into a new virtual environment, run `noxusai --version`,
   and execute JSON doctor for the website workflow.

Example post-publication verification:

```bash
python -m venv /tmp/noxus-release-check
/tmp/noxus-release-check/bin/python -m pip install --no-cache-dir noxusai==1.0.0rc1
/tmp/noxus-release-check/bin/noxusai --version
/tmp/noxus-release-check/bin/noxusai --json doctor --workflow website
gh attestation verify noxusai-1.0.0rc1-py3-none-any.whl \
  --repo 5bv57zcm44-max/noxus-core
```

On Windows, create a new directory-backed virtual environment and use its
`Scripts\\python.exe` and `Scripts\\noxusai.exe` paths. Do not test by upgrading an existing
development or Frappe Bench environment.

## Failure policy

PyPI versions and Git tags are immutable. If publication partially succeeds, do not delete or
overwrite the published version. Stop, preserve the workflow logs and artifact hashes, document the
partial state, correct the fault, increment the version, rerun every gate, and publish a new
candidate. A failed trusted-publisher exchange is an identity/configuration error, not a reason to
fall back to a long-lived token.
