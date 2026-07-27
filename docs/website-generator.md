# Website backend generator

`noxusai new website` renders only selected apps with Jinja `StrictUndefined`. Project names are
validated lowercase slugs, every output path is resolved below the destination, and generation is
staged atomically. Docker always selects PostgreSQL; SQLite is local-development only.

Generated APIs use `/api/v1`, JWT and/or session authentication, page-number pagination, filtering,
OpenAPI at `/api/schema/`, Swagger at `/api/docs/`, ReDoc at `/api/redoc/`, and live/readiness at
`/health/live/` and `/health/ready/`. Public contact, newsletter, and analytics writes use scoped
throttling. Integrate a spam provider in the public-form serializer or view without placing provider
credentials in generated source.

Translated values retain `{en, ar}` object shape. `Accept-Language` adds resolved display fields;
project language limits accepted keys. Upload extensions and a 10 MiB limit are enforced server-side.

`.noxus/template-lock.json` stores generator version and file hashes. `noxusai update` replaces only
files still matching their previous generated hash. User changes are listed in
`.noxus/update-plan.yml` and never overwritten.
