# Deployment Guide

This guide covers deploying Campus Connect to a production server using Docker Compose (the
simplest path), plus notes for adapting to managed cloud services.

## 1. Prerequisites

- A server (VM, VPS, or cloud instance) with Docker Engine 24+ and the Docker Compose plugin installed.
- A domain name pointed at the server (recommended, for HTTPS).
- (Optional but recommended) A Google Maps API key with the **Distance Matrix API** enabled, if you
  want real road-network route data instead of the built-in heuristic estimator.

## 2. Clone and configure

```bash
git clone <this-repo> campus-connect
cd campus-connect
cp .env.example .env
```

Edit `.env`:

| Variable | Notes |
|---|---|
| `SECRET_KEY` | **Must** be a long random string in production. Generate with `openssl rand -hex 32`. Never reuse the dev default. |
| `POSTGRES_PASSWORD` | Use a strong, unique password. |
| `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` | The admin account created on first boot. Change the password immediately after first login if you keep the default email. |
| `CORS_ORIGINS` | Set to your actual frontend origin(s), e.g. `https://campusconnect.example.com`. |
| `GOOGLE_MAPS_API_KEY` | Optional. Enables real Distance Matrix data for route search. |
| `AMAZON_*`, `FLIPKART_*`, `ZOMATO_API_KEY`, `SWIGGY_API_KEY` | Optional. See the "External API integrations" section in the main README — these platforms require approved affiliate/partner accounts and are typically synced via a separate scheduled job rather than called live. |

## 3. Build and start

```bash
docker compose up --build -d
```

This will:
1. Start Postgres and Redis, waiting for their healthchecks to pass.
2. Build and start the backend, whose entrypoint script waits for Postgres, runs
   `alembic upgrade head`, and runs the idempotent seed script (creates the admin account and demo
   data on first run only — safe to re-run on every deploy).
3. Build and start the frontend (nginx serving the compiled React app, reverse-proxying `/api/*` to
   the backend).

Check everything is healthy:

```bash
docker compose ps
curl http://localhost:8000/health
```

## 4. Put HTTPS in front of it

Docker Compose here exposes the frontend on port 80 and the backend directly on port 8000. For a
real deployment, put a TLS-terminating reverse proxy in front — either:

- **Managed**: a load balancer (AWS ALB, GCP Load Balancer, etc.) with a managed certificate, or
- **Self-hosted**: [Caddy](https://caddyserver.com/) or [Traefik](https://traefik.io/) in front of
  the `frontend` service, or [nginx + certbot](https://certbot.eff.org/) on the host.

Either way:
- Only the `frontend` service (port 80) needs to be publicly reachable — it already proxies `/api/*`
  to the backend internally over the Docker network.
- Consider removing the public port mapping for `backend` (`8000:8000`) and `postgres`/`redis` in
  `docker-compose.yml` once you've confirmed everything works, so only the frontend is internet-facing.
- Update `CORS_ORIGINS` in `.env` to your real HTTPS origin.

## 5. Database migrations on future deploys

The backend's `entrypoint.sh` runs `alembic upgrade head` automatically on every container start, so
a normal `docker compose up --build -d` after pulling new code will apply any new migrations. To
create a new migration after changing a model:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe your change"
docker compose exec backend alembic upgrade head
# Commit the new file under backend/alembic/versions/
```

## 6. Backups

Postgres data is persisted in the `postgres_data` named volume. Back it up regularly, e.g.:

```bash
docker compose exec postgres pg_dump -U campus campus_connect > backup-$(date +%F).sql
```

Restore with:

```bash
cat backup-2026-08-21.sql | docker compose exec -T postgres psql -U campus campus_connect
```

## 7. Scaling notes

- The backend is stateless (all session state lives in Postgres/Redis), so you can run multiple
  backend replicas behind a load balancer. Increase `--workers` in the backend `Dockerfile`'s `CMD`
  or run multiple container replicas.
- Redis is used for route-search caching and JWT blacklisting — both tolerate a cold cache fine, so
  Redis doesn't need to be highly available for correctness, just for performance.
- Postgres is the only stateful, single-point-of-failure component in this compose file. For a real
  production deployment, consider a managed Postgres service (RDS, Cloud SQL, etc.) with automated
  backups and failover instead of the single-container setup here.

## 8. Environment-specific alternatives

If you'd rather not run Docker Compose directly on a VM:

- **Backend**: any container platform (ECS, Cloud Run, Fly.io, Railway) works as-is — it's a
  standard stateless FastAPI container reading config from environment variables.
- **Frontend**: since it's a static build served by nginx, it can equally be deployed to any static
  host (Vercel, Netlify, Cloudflare Pages, S3+CloudFront) — just set `VITE_API_BASE_URL` at build
  time to your backend's public URL instead of the relative `/api/v1` used in the nginx-proxy setup.
- **Database/Redis**: swap for managed equivalents (RDS/Cloud SQL for Postgres, ElastiCache/Memorystore
  for Redis) by just changing `DATABASE_URL` / `REDIS_URL` — no code changes needed.
