# Deployment, backup, and recovery

Production uses `docker compose --profile production up --build --detach`. MariaDB, three Redis
roles, backend, short/long workers, scheduler, websocket, proxy, site creator, named volumes, and
health checks are explicit. Proxy hostnames are allow-listed and UI/API/files/assets/websockets share
one origin. Image index and per-platform digests are recorded in `container-digests.lock.yml`.

Terminate TLS at a trusted edge proxy and forward only the allow-listed host plus
`X-Forwarded-Proto: https`. Production website projects additionally require
`NOXUS_DEPLOYMENT_PROFILE=production`, real `DJANGO_ALLOWED_HOSTS`, CORS/CSRF origins, and the
`compose.production.yaml` override. Never expose database, Redis, backend, or worker ports publicly.

Run `noxusai backup` before upgrades. Restore requires `--archive`, the exact site/database target,
interactive confirmation or `--yes --confirm-target`, and automatically creates a safety backup.
Upgrades build a new image, run preflight, retain the previous image and backup, migrate, then health
check. Rollback is explicit; NOXUS never silently destroys volumes.

Community Deploy applies to the current site or exports the blueprint/configuration and exact Docker
commands. It does not provision cloud infrastructure.
