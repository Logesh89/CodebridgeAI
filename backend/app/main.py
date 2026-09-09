"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging
from app.core.exceptions import AppException
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.schemas import HealthResponse

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    for directory in [
        settings.upload_dir,
        settings.snaplogic_json_dir,
        settings.generated_dir,
        settings.completed_dir,
        settings.failed_dir,
        settings.logs_dir,
        settings.reports_dir,
        settings.temp_dir,
        settings.downloads_dir,
    ]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Application started: %s", settings.app_name)
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    description="AI-powered CodeBridge AI conversion platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(ExceptionHandlerMiddleware)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "errors": exc.details},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "online",
        "message": "CodeBridge AI Platform Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.api_v1_prefix,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    db_status = "healthy"
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="1.0.0",
        database=db_status,
        redis="not_configured",
    )

