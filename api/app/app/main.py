"""FastAPI application entry point."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import Base, get_engine
from app.core.logging_config import setup_logging
from app.core.exceptions import AppException
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.schemas import HealthResponse

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    is_vercel = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    base_dir = "/tmp" if is_vercel else "."

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
        try:
            target_path = Path(base_dir) / directory if is_vercel else Path(directory)
            target_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning("Could not create directory %s: %s", directory, e)

    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error("Error creating database tables: %s", e)

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    db_status = "healthy"
    try:
        engine = get_engine()
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
