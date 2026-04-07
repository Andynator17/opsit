# OpsIT — Deployment Guide

Specific to this VPS setup:

| Existing container  | Role                                                         |
|---------------------|--------------------------------------------------------------|
| `traefik-nhwc`      | Reverse proxy (`network_mode: host`, ports 80/443 + ACME)    |
| `n8n-irio`          | n8n, routed via Traefik as `n8n.hitex.at`                    |
| `postgresql-cjc4`   | Separate Postgres (NOT used by OpsIT)                        |

OpsIT adds its own Postgres + backend + frontend, all under
`opsit-dev.hitex.at`. Path-based routing (Variant A):

```
https://opsit-dev.hitex.at/         -> opsit-frontend  (SPA via nginx)
https://opsit-dev.hitex.at/api/...  -> opsit-backend   (FastAPI)
```

Same origin → no CORS, no extra DNS records, one Let's Encrypt cert.

## Why no extra Traefik network?

Your Traefik runs in `network_mode: host`, so it isn't attached to any
docker bridge network. Instead it discovers containers via the docker
socket and reaches them via their bridge IP (which is routable from the
host network namespace).

This compose file creates a private bridge network `opsit_web` and
attaches frontend + backend to it. The label
`traefik.docker.network=opsit_web` tells Traefik which IP to use.

**Nothing to pre-create on the host.** No `docker network create`.

---

## 1. DNS (already done by you)

```
opsit-dev.hitex.at  A   <vps-ipv4>
n8n.hitex.at        A   <vps-ipv4>
```

## 2. Clone the repo on the VPS

```bash
cd /opt
sudo git clone https://github.com/Andynator17/opsit.git
sudo chown -R $USER:$USER opsit
cd opsit
```

## 3. Configure secrets

```bash
cp .env.example .env

openssl rand -hex 32      # → paste into SECRET_KEY
openssl rand -base64 24   # → paste into POSTGRES_PASSWORD

nano .env
```

Required edits:
- `POSTGRES_PASSWORD` (must match the password in `DATABASE_URL`!)
- `SECRET_KEY`
- `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`

`DOMAIN_OPSIT` and `VITE_API_URL` are already correct in the example.

## 4. Build & start

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f backend
```

On first start:
- `opsit-postgres` initializes the database
- `opsit-backend` runs `alembic upgrade head` automatically, then starts uvicorn
- Traefik picks up the new containers via docker socket within ~2 seconds
- Traefik requests a Let's Encrypt cert for `opsit-dev.hitex.at`
  (HTTP-01 challenge → port 80 → DNS must already resolve)

Watch Traefik for cert acquisition:

```bash
docker logs -f traefik-nhwc | grep -i 'acme\|cert\|opsit'
```

## 5. Verify

```bash
# from the VPS or anywhere:
curl -I https://opsit-dev.hitex.at/
curl    https://opsit-dev.hitex.at/api/v1/openapi.json | head -c 200
```

Then open `https://opsit-dev.hitex.at` in a browser, log in with
`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD`, and **change the
password immediately**.

## 6. (Optional) Let n8n call OpsIT internally

If you want n8n workflows to hit OpsIT directly without going through
the public internet:

```bash
docker network connect opsit_web n8n-irio
```

In n8n HTTP Request nodes you can then use:
```
http://opsit-backend:8000/api/v1/...
```

No TLS, no public DNS, no rate-limiting from outside. Authenticate
normally with a JWT (`Authorization: Bearer <token>` from
`/api/v1/auth/login`).

Verify both are on the network:
```bash
docker network inspect opsit_web --format '{{range .Containers}}{{.Name}}{{"\n"}}{{end}}'
# expected: opsit-backend, opsit-frontend, n8n-irio
```

---

## Day-2 operations

### Update the app

```bash
cd /opt/opsit
git pull
docker compose build backend frontend
docker compose up -d
```

Traefik untouched.

### Tail logs

```bash
docker compose logs -f backend
docker compose logs -f opsit-postgres
```

### Database backup

```bash
docker compose exec opsit-postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  | gzip > backup-$(date +%F).sql.gz
```

Restore:
```bash
gunzip -c backup-YYYY-MM-DD.sql.gz | \
  docker compose exec -T opsit-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Cron entry (`crontab -e`):
```cron
0 3 * * * cd /opt/opsit && docker compose exec -T opsit-postgres pg_dump -U opsit opsit | gzip > /opt/opsit/backups/db-$(date +\%F).sql.gz
```

### Persistent volumes

| Volume            | Holds                          |
|-------------------|--------------------------------|
| `postgres_data`   | OpsIT database files           |
| `backend_uploads` | User-uploaded files            |

Back these up regularly.

---

## Troubleshooting

| Symptom                                              | Likely cause / fix                                                                                  |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `connection refused` from Traefik to backend         | `traefik.docker.network=opsit_web` label missing or wrong; container not on `opsit_web`             |
| Browser hangs on https with cert error               | DNS hasn't propagated yet, or Let's Encrypt rate-limit; check `docker logs traefik-nhwc`            |
| `Bad Gateway` from Traefik on `/api/...`             | Backend not started/healthy. `docker compose logs backend`                                          |
| `404` on `/` but `/api/v1/docs` works (or vice versa)| Router rule mismatch; check `priority` labels in compose                                            |
| Backend exits with `connection refused` to db        | `.env` `DATABASE_URL` password ≠ `POSTGRES_PASSWORD`                                                |
| Frontend shows API errors after deploy               | `VITE_API_URL` was wrong at build time → `docker compose build frontend && up -d frontend`          |
| Alembic fails on startup                             | `docker compose logs backend`; fix the migration, then `up -d` again                                |
| n8n can't reach `http://opsit-backend:8000`          | `docker network connect opsit_web n8n-irio`                                                         |
