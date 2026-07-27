# NOXUS container runtime

This runtime builds the exact pinned Frappe source plus the bundled NOXUS apps into a local image.
Select `--profile development` or `--profile production`; both use the same service topology while
environment files control exposure and policy. No public image tag is trusted as a NOXUS runtime.

The initial administrator credential is consumed from a Compose secret or the protected
`NOXUS_ADMIN_PASSWORD` environment value and is never accepted as a CLI argument.
