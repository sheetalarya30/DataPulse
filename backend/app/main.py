from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import (
    DataPulseException,
    datapulse_exception_handler,
    generic_exception_handler,
)
from app.db.init_db import init_db, seed_reproducible_data
from app.db.session import SessionLocal
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize tables and seed baseline data
    logger.info("Starting DataPulse Platform Backend...")
    try:
        init_db()
        with SessionLocal() as db:
            seed_reproducible_data(db)
    except Exception as e:
        logger.error(f"Error during database initialization/seeding: {e}")
    yield
    logger.info("Shutting down DataPulse Platform Backend.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Data Pipeline Monitoring, Diagnosis, and Recovery Platform API.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(DataPulseException, datapulse_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API Router
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "Detect. Diagnose. Recover.",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "dashboard_summary_url": "/api/dashboard/summary",
    }
