from fastapi import APIRouter
from app.api.routes import (
    health,
    dashboard,
    pipelines,
    runs,
    incidents,
    quality,
    recovery,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(health.router)
api_router.include_router(dashboard.router)
api_router.include_router(pipelines.router)
api_router.include_router(runs.router)
api_router.include_router(incidents.router)
api_router.include_router(quality.router)
api_router.include_router(recovery.router)

