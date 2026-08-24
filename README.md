# Campus Connect

Campus Connect helps students who are new to a city find the best way to reach their college from a
railway station, airport, or bus stand — with metro, bus, cab, auto, walking, and mixed route options,
each with distance, estimated time, estimated cost, and turn-by-turn steps. Beyond routing, it's a
one-stop hub for college info, local student services (PGs, mess, medical stores, ATMs, grocery),
a student offers dashboard, and a review/tips community.

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Quick start (Docker)](#quick-start-docker)
- [Local development (without Docker)](#local-development-without-docker)
- [Running tests](#running-tests)
- [External API integrations](#external-api-integrations)
- [Architecture notes](#architecture-notes)
- [Deployment](#deployment)

## Features

1. **Authentication** — signup/login, JWT access + refresh tokens (with rotation and revocation), profile management, RBAC (student/admin).
2. **Route Finder** — search by source (railway station / airport / bus stand) + college, returns metro, bus, cab, auto, walking, and mixed routes, each with distance, time, cost, and steps, rendered on an interactive map-ready UI.
3. **College Information** — location, nearby landmarks, emergency contacts.
4. **Local Student Services** — PGs, hostels, mess facilities, medical stores, ATMs, grocery stores near each college.
5. **Offers Dashboard** — Zomato, Swiggy, Amazon, and Flipkart deals, filterable by platform/category, with promo-code copy.
6. **Reviews & Community** — college/PG/hostel/route reviews with star ratings, and a student tips board.
7. **Saved Routes** — bookmark routes and browse full search history.
8. **Admin Dashboard** — manage colleges, offers, users (roles/activation), and view platform analytics.

## Tech stack

| Layer        | Technology |
|--------------|------------|
| Frontend     | React 18, TypeScript, Tailwind CSS, shadcn/ui (Radix primitives), React Query, React Router |
| Backend      | FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, JWT (python-jose), bcrypt |
| Database     | PostgreSQL 16 |
| Caching      | Redis 7 (route-search caching, token blacklist) |
| Deployment   | Docker, Docker Compose, nginx (frontend reverse proxy) |

## Project structure

```
campus-connect/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security, redis, logging, exceptions
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── repositories/   # Repository pattern - all raw queries live here
│   │   ├── services/       # Business logic, orchestrates repositories
│   │   ├── api/v1/         # FastAPI routers (thin - delegate to services)
│   │   └── main.py         # App entrypoint
│   ├── alembic/             # DB migrations
│   ├── scripts/seed.py      # Idempotent first-run admin + demo data seeding
│   ├── tests/                # pytest suite (runs against a real Postgres test DB)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # ui/ (shadcn primitives), layout/, routes/, reviews/
│   │   ├── pages/           # One file per route
│   │   ├── hooks/            # React Query hooks per feature area
│   │   ├── context/          # AuthContext
│   │   ├── lib/               # api-client, api/* typed wrappers, utils
│   │   └── types/             # Shared TypeScript types mirroring backend schemas
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

## Quick start (Docker)

This is the fastest way to run the full stack.

```bash
git clone <this-repo> campus-connect
cd campus-connect
cp .env.example .env
# Edit .env: at minimum set SECRET_KEY and FIRST_ADMIN_PASSWORD to real values.
# Generate a strong secret with: openssl rand -hex 32

docker compose up --build
```

Once containers are healthy:

- Frontend: http://localhost
- Backend Swagger docs: http://localhost:8000/docs (also proxied at http://localhost/docs)
- Backend health check: http://localhost:8000/health

On first boot, the backend container automatically runs Alembic migrations and seeds:
- An admin account (`FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` from your `.env`)
- Two demo colleges, a couple of PG listings, local services, and four demo offers

so the app isn't empty on first launch.

> **Note on this repository's Docker files:** the Dockerfiles and `docker-compose.yml` follow
> standard, widely-used patterns (multi-stage builds, non-root users, healthchecks, dependency
> ordering) and the app code itself has been extensively tested against real Postgres/Redis
> instances and a real production build — but the Docker images were not built inside this
> generation environment (no Docker daemon was available here). Please run `docker compose up
> --build` yourself and open an issue/adjust if you hit anything environment-specific.

## Local development (without Docker)

### Backend

```bash
cd backend 
python -m venv .venv && .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env
# Point DATABASE_URL / DATABASE_URL_SYNC at a local Postgres instance,
# and REDIS_URL at a local Redis instance.

alembic upgrade head
python -m scripts.seed          # optional but recommended - creates admin + demo data

uvicorn app.main:app --reload   # http://localhost:8000, docs at /docs
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=/api/v1 works out of the box with the Vite dev proxy
npm run dev                     # http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` (configurable via
`VITE_API_PROXY_TARGET`), so the frontend talks to your locally running backend without any CORS setup.

## Running tests

Backend tests run against a **real** Postgres database (not SQLite), because several models use
Postgres-native types (`UUID`, `JSONB`, `ARRAY`) that SQLite can't represent. Each test function gets
a fresh schema for full isolation.

```bash
cd backend
createdb campus_connect_test   # or: psql -c "CREATE DATABASE campus_connect_test OWNER campus;"
pytest                          # 23 tests covering auth, RBAC, route search, bookmarking, reviews
```

## External API integrations

Campus Connect is designed to degrade gracefully when third-party credentials aren't configured,
and to automatically use them once they are:

- **Google Maps / Directions / Places** — set `GOOGLE_MAPS_API_KEY` and the route finder
  automatically switches from its built-in haversine-distance heuristic estimator to real Google
  Distance Matrix data. Without a key, routes are still fully functional using realistic Indian
  urban travel-time/cost heuristics (see `backend/app/services/routing_engine.py`).
- **Amazon Affiliate API / Flipkart Affiliate API** — both require signed requests and an approved
  affiliate account, so they can't be called anonymously. The `offers` table is the single source
  of truth the frontend reads from regardless of where the data originates; in production, wire a
  scheduled job (Celery beat / cron) that calls the affiliate APIs with your credentials
  (`AMAZON_*` / `FLIPKART_*` env vars are already wired into settings) and upserts into `offers`.
  Until then, admins manage offers manually via the Admin Dashboard.
- **Zomato / Swiggy** — neither currently exposes a public partner API for third-party discount
  aggregation. The same `offers` table + Admin Dashboard pattern applies; `ZOMATO_API_KEY` /
  `SWIGGY_API_KEY` are wired into settings for whenever/if that changes.

## Architecture notes

- **Clean architecture / layering**: routers → services → repositories → models. Routers contain no
  business logic; services contain no raw SQL; repositories contain no business rules.
- **Dependency injection**: all repositories and services are constructed via FastAPI's `Depends` in
  `app/api/deps.py`, so swapping an implementation (e.g. for tests) means overriding one function.
- **RBAC**: `require_role(*roles)` in `app/api/deps.py` is a reusable guard; admin-only endpoints
  depend on it directly.
- **JWT**: short-lived access tokens (30 min default) + longer-lived refresh tokens (7 days default)
  with rotation — each refresh call blacklists the previous refresh token's `jti` in Redis, and
  logout blacklists the current one.
- **Caching**: route-search results are cached in Redis for 30 minutes per unique
  (source, source_type, college) combination, since Directions API calls are the most expensive
  external dependency in the request path.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for a step-by-step production deployment guide.
