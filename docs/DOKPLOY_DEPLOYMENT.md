# Dokploy Deployment Guide

Deploy Talisik Short URL to a self-hosted [Dokploy](https://dokploy.com) instance
using the repo's `Dockerfile`. No app code changes are required — Dokploy builds
and runs the container, and Traefik (bundled with Dokploy) handles routing and
Let's Encrypt TLS for your domain.

## Prerequisites

- A running Dokploy instance with access to its dashboard.
- A Supabase project with `supabase/schema.sql` already applied (see the main
  README / migration notes for that step).
- Your Supabase **Transaction pooler** connection string
  (Project Settings > Database > Connection string), port `6543`.

## 1. Create the application

In the Dokploy dashboard:

1. **Create Project** (or reuse an existing one) → **Create Application**.
2. **Source**: connect the Git repository for this project, branch `main`.
3. **Build Type**: `Dockerfile` (the repo's root `Dockerfile` builds and starts
   the app via gunicorn + uvicorn workers on port `8080` — see `Dockerfile` and
   `start.sh`).
4. **Port**: `8080` (matches `EXPOSE 8080` / the gunicorn `--bind` in the
   Dockerfile).

## 2. Set environment variables

In the application's **Environment** tab, set these directly in Dokploy —
**never commit real values to the repo** (`env.example`/`env.downlodr` are
placeholder templates only, and `env.downlodr` is gitignored on purpose):

```env
BASE_URL=https://go.downlodr.com
STORAGE_BACKEND=supabase

# Supabase transaction pooler URI (contains the DB password — dashboard-only)
SUPABASE_DB_URL=postgresql://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres

CORS_ORIGINS=https://go.downlodr.com,https://downlodr.com,https://www.downlodr.com

DEBUG=false
LOG_LEVEL=WARNING
ENVIRONMENT=production

DEFAULT_CODE_LENGTH=7
MAX_CUSTOM_CODE_LENGTH=50
ENABLE_ANALYTICS=true
ENABLE_EXPIRATION=true

RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

Adjust `BASE_URL`/`CORS_ORIGINS` to whatever domain you point at this app.

## 3. Deploy

Trigger a deploy from the Dokploy dashboard (or push to the connected branch if
auto-deploy is enabled). Dokploy builds the `Dockerfile`, starts the container,
and exposes it internally on port `8080`.

## 4. Add your domain

In the application's **Domains** tab:

1. Add `go.downlodr.com` (or your chosen domain).
2. Point its DNS `A`/`CNAME` record at your Dokploy host per the dashboard's
   instructions.
3. Enable **HTTPS** — Dokploy provisions a Let's Encrypt certificate via
   Traefik automatically once DNS resolves.

## 5. Verify

```bash
export APP_URL="https://go.downlodr.com"

# API root
curl "$APP_URL/"

# Shorten a URL
curl -X POST "$APP_URL/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/frederickluna/talisik-short-url"}'

# Redirect (use the short_code from the previous response)
curl -I "$APP_URL/SHORT_CODE"
```

## Notes

- The app holds a Postgres connection pool in-process (`SupabaseStorage` in
  `talisik/core/storage.py`); that requires a long-running container, which is
  exactly what Dokploy runs — no serverless cold-start/connection-reuse
  caveats to worry about here.
- `HEALTHCHECK` is defined in the `Dockerfile` (`GET /`) — Dokploy/Traefik can
  use container health status for zero-downtime rolling deploys if configured.
