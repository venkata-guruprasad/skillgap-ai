"""API route registration package."""

from fastapi import APIRouter

from app.routes.analysis import router as analysis_router
from app.routes.auth import router as auth_router
from app.routes.career import router as career_router
from app.routes.dashboard import router as dashboard_router
from app.routes.health import router as health_router
from app.routes.jobs import router as jobs_router
from app.routes.resume import router as resume_router
from app.routes.roadmap import router as roadmap_router
from app.routes.skills import router as skills_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(resume_router)
api_router.include_router(skills_router)
api_router.include_router(jobs_router)
api_router.include_router(analysis_router)
api_router.include_router(career_router)
api_router.include_router(roadmap_router)

__all__ = ["api_router"]
