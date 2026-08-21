"""
CampusNest API — FastAPI application entrypoint.

Run from the project root:
    uvicorn backend.main:app --reload --port 8000
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine
from .routers import (
    analytics,
    auth,
    community,
    moderator,
    owner,
    payments,
    profiles,
    properties,
    reviews,
    roommates,
    services,
    transport,
)
from .seed import seed_if_empty

logging.basicConfig(level=logging.INFO if settings.DEBUG else logging.WARNING,
                    format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("campusnest")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.SEED_DEMO_DATA and seed_if_empty():
        log.info("Demo data seeded into %s", settings.sqlalchemy_url)
    log.info("%s ready — docs at /docs", settings.APP_NAME)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Student Housing & Community Platform API — property discovery, roommate matching, "
        "community hub, rent analytics, transport sharing, owner & moderator tools."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in settings.ALLOWED_ORIGINS else settings.ALLOWED_ORIGINS,
    allow_credentials="*" not in settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, profiles, properties, reviews, community, roommates, transport,
          analytics, services, owner, moderator, payments):
    app.include_router(r.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "demo": {
            "student": {"reg_no": "21BCE0001", "otp": settings.DEMO_OTP if settings.DEBUG else "sent via SMS"},
            "owner": {"phone": "+919800000001", "otp": settings.DEMO_OTP if settings.DEBUG else "sent via SMS"},
            "moderator": {"phone": settings.MODERATOR_PHONE, "otp": settings.DEMO_OTP if settings.DEBUG else "sent via SMS"},
        } if settings.DEBUG else None,
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "database": "sqlite" if settings.USE_SQLITE else "postgresql",
            "payments_enabled": settings.payments_enabled}
