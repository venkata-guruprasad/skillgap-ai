"""FastAPI application entry point for SkillGap AI."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import SessionLocal, check_db_connection, init_db
from app.models.user import User
from app.routes import api_router
from app.services.job_service import seed_sample_jobs
from app.utils.logger import configure_logging
from app.utils.security import hash_password

logger = configure_logging(debug=settings.effective_debug)


def _seed_initial_data() -> None:
    """Seed the local dev demo student account (dev only) and the 8 labeled sample job descriptions."""
    if SessionLocal is None:
        return

    db = SessionLocal()
    try:
        if not settings.is_production:
            demo_email = "alex.rivera@university.edu"
            existing = db.query(User).filter(User.email == demo_email).first()
            if existing is None:
                db.add(
                    User(
                        email=demo_email,
                        full_name="Alex Rivera",
                        hashed_password=hash_password("demo-password-2026"),
                        role="student",
                        is_active=True,
                    )
                )
                db.commit()
                logger.info("Seeded development demo account: %s", demo_email)

        seed_sample_jobs(db)
    except Exception as exc:
        db.rollback()
        logger.warning("Skipping initial data seed: %s", exc.__class__.__name__)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle events."""
    settings.validate_production_config()
    logger.info(
        "Starting %s v%s (env=%s, debug=%s)",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
        settings.effective_debug,
    )
    init_db()
    db_ok, db_msg = check_db_connection()
    if db_ok:
        logger.info("Database check: %s", db_msg)
        _seed_initial_data()
    else:
        logger.warning("Database check: %s", db_msg)
    yield
    logger.info("Shutting down %s", settings.APP_NAME)


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application instance."""
    docs_enabled = settings.ENABLE_API_DOCS or not settings.is_production

    application = FastAPI(
        title=f"{settings.APP_NAME} API",
        description=(
            "Backend API for SkillGap AI – AI-Powered Skill Gap & Career Prediction System."
        ),
        version=settings.APP_VERSION,
        debug=settings.effective_debug,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    @application.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security", "max-age=31536000; includeSubDomains"
            )
        return response

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled error on %s %s: %s",
            request.method,
            request.url.path,
            exc.__class__.__name__,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )

    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @application.get("/", tags=["Root"])
    def root() -> dict[str, str]:
        return {
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs" if docs_enabled else "disabled",
            "health": f"{settings.API_V1_PREFIX}/health",
        }

    return application


app = create_app()
