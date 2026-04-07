# OpsIT — Deployment Guide (sidecar to existing Traefik + n8n)

This stack assumes the VPS **already runs**:

- a **Traefik** container `traefik-nhwc` handling host ports 80/443 + TLS
- an **n8n** container `n8n-irio`

OpsIT plugs into the existing Traefik via a shared Docker network and
Traefik labels. It brings only its own Postgres, backend, frontend, and
landing page — nothing that would collide with what's already running.

## Stack overview (added by this repo)

| Service       | Container name    | Image / Build         | Internal port | Routed by Traefik to |
|---------------|-------------------|-----------------------|---------------|----------------------|
| `postgres`    | `opsit-postgres`  | `postgres:16-alpine`  | 5432          | — (internal only)    |
| `backend`     | `opsit-backend`   | `./backend`           | 8000          | `api.example.com`    |
| `frontend`    | `opsit-frontend`  | `./frontend`          | 80            | `app.example.com`    |
| `landingpage` | `opsit-landing`   | `./landingpage`       | 80            | `example.com`        |

**No host ports are published.** Traefik routes via Docker labels.

---

## 1. Identify the Traefik network, entrypoint, and certresolver

OpsIT must join the same Docker network as `traefik-nhwc`, and its
labels must reference the right entrypoint + certresolver names.

**Network name:**
```bash
docker inspect traefik-nhwc \
  --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}'
```
Common names: `traefik`, `proxy`, `web`, `traefik_default`.

**Entrypoint + certresolver** — look at how Traefik itself was started.
Usually visible in its compose file or `traefik.yml` static config:
```bash
docker inspect traefik-nhwc --format '{{range .Args}}{{println .}}{{end}}' \
  | grep -E 'entryPoints|certificatesResolvers'
```
Look for things like `--entryPoints.websecure.address=:443` and
`--certificatesResolvers.letsencrypt.acme...`. The names after the dot
(`websecure`, `letsencrypt` in this example) are what you need.

If your names differ from the defaults (`traefik` / `websecure` /
`letsencrypt`), put them in `.env`:
```ini
TRAEFIK_NETWORK=proxy
TRAEFIK_ENTRYPOINT=https
TRAEFIK_CERTRESOLVER=myresolver
```

> If `TRAEFIK_NETWORK` is not `traefik`, you must also change the
> `name:` field at the bottom of [docker-compose.yml](docker-compose.yml)
> to match — env vars can't be used in the `networks:` external `name:`
> field.

## 2. Make sure n8n-irio is on the same network

You want n8n workflows to call OpsIT directly. One command:

```bash
docker network connect <traefik-network-name> n8n-irio
```

(e.g. `docker network connect traefik n8n-irio`)

Verify:
```bash
docker network inspect <traefik-network-name> \
  --format '{{range .Containers}}{{.Name}}{{"\n"}}{{end}}'
# expected (after step 6): traefik-nhwc, n8n-irio, opsit-backend, opsit-frontend, opsit-landing
```

In n8n HTTP Request nodes, use as base URL:
```
http://opsit-backend:8000/api/v1/...
```
No TLS, no public DNS, no Traefik in the way. Authenticate normally
with a JWT (`Authorization: Bearer <token>`).

## 3. DNS

Three A records pointing to the VPS IP:
```
example.com         A   <vps-ip>
app.example.com     A   <vps-ip>
api.example.com     A   <vps-ip>
```

## 4. Clone the repo

```bash
cd /opt
sudo git clone <your-git-url> opsit
sudo chown -R $USER:$USER opsit
cd opsit
```

## 5. Configure secrets

```bash
cp .env.example .env

openssl rand -hex 32      # → SECRET_KEY
openssl rand -base64 24   # → POSTGRES_PASSWORD

nano .env
```

Required edits in `.env`:
- `DOMAIN_APP`, `DOMAIN_API`, `DOMAIN_LANDING`
- `TRAEFIK_NETWORK`, `TRAEFIK_ENTRYPOINT`, `TRAEFIK_CERTRESOLVER` (only if non-default)
- `POSTGRES_PASSWORD` (must match the password in `DATABASE_URL`!)
- `SECRET_KEY`
- `BACKEND_CORS_ORIGINS` — e.g. `https://app.example.com,https://example.com`
- `VITE_API_BASE_URL` — e.g. `https://api.example.com` (build-time!)
- `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` — change after first login

## 6. Build & start OpsIT

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f backend
```

Backend runs `alembic upgrade head` automatically on startup. Traefik
picks up the new containers and their labels within a few seconds —
**no Traefik reload needed**, that's the whole point of label-based
discovery.

## 7. Verify

```bash
curl -I https://example.com
curl -I https://app.example.com
curl    https://api.example.com/health
```

n8n → OpsIT internal:
```bash
docker exec n8n-irio wget -qO- http://opsit-backend:8000/health
# expected: {"status":"healthy",...}
```

Then log into `https://app.example.com` with `FIRST_ADMIN_EMAIL` /
`FIRST_ADMIN_PASSWORD` and **change the password immediately**.

If TLS for the new domains takes a moment: watch Traefik:
```bash
docker logs -f traefik-nhwc | grep -i 'acme\|cert'
```

---

## Day-2 operations

### Update the app
```bash
cd /opt/opsit
git pull
docker compose build backend frontend landingpage
docker compose up -d
```
(Traefik untouched.)

### Tail logs
```bash
docker compose logs -f backend
docker compose logs -f postgres
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
| `backend_uploads` | User uploads from OpsIT API    |

Back these up regularly.

---

## Troubleshooting

| Symptom                                              | Likely cause / fix                                                                                  |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `network traefik declared as external, but ...`     | Network doesn't exist or has a different name. `docker network ls`, then update compose `name:`     |
| Traefik dashboard shows the routers but `404`        | Container not on the same docker network as Traefik, or `traefik.docker.network` label is wrong    |
| Traefik shows the router but `Bad Gateway`           | Wrong `loadbalancer.server.port`. Backend = 8000, frontend/landing = 80                            |
| No HTTPS / `default certificate`                     | Wrong `TRAEFIK_CERTRESOLVER` name; check Traefik static config for the actual resolver name        |
| `404` from Traefik on the new domain                 | Wrong `TRAEFIK_ENTRYPOINT` name (must match Traefik static config) or DNS not propagated            |
| n8n can't reach `http://opsit-backend:8000`          | n8n-irio isn't on the Traefik network. `docker network connect <net> n8n-irio`                     |
| Backend exits with `connection refused` to db        | `.env` `DATABASE_URL` password ≠ `POSTGRES_PASSWORD`                                                |
| Frontend shows API errors after deploy               | `VITE_API_BASE_URL` was wrong at build time → `docker compose build frontend && up -d frontend`     |
| CORS error in browser                                | Add the frontend origin to `BACKEND_CORS_ORIGINS` in `.env`, then `up -d backend`                  |
| Alembic fails on startup                             | `docker compose logs backend`; fix the migration, then `up -d` again                                |
