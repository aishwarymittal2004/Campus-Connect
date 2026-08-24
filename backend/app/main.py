"""
Campus Connect API entrypoint.

Run locally with:  uvicorn app.main:app --reload
Docs (Swagger UI):  http://localhost:8000/docs
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging, get_logger
from app.core.redis_client import cache

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app_env=settings.APP_ENV)
    redis_ok = await cache.ping()
    logger.info("redis_connection", ok=redis_ok)
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Campus Connect: helps students new to a city find the best way to reach their "
        "college from a railway station, airport, or bus stand - plus college info, local "
        "student services, community reviews, saved routes, and a student offers dashboard."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


@app.get("/health", tags=["Health"])
async def health_check():
    redis_ok = await cache.ping()
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV, "redis": redis_ok}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
