# Tutorial: company website backend

Run `noxusai new website --name acme-web --database postgres --auth both --docker --yes`, create the
two secret files referenced by Compose, then `docker compose up --build`. Visit `/api/docs/`, create
content through admin, and request it with `Accept-Language: ar` to verify resolved Arabic fields.
